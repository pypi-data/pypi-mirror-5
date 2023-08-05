# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from uuid import uuid1 as new_uuid

from seantis.reservation.tests import IntegrationTestCase
from seantis.reservation.error import (
    OverlappingAllocationError,
    AffectedReservationError,
    AlreadyReservedError,
    ReservationTooLong,
    InvalidReservationError,
    InvalidAllocationError
)

from seantis.reservation import utils
from seantis.reservation.session import serialized
from seantis.reservation import events

from seantis.reservation import db
Scheduler = db.Scheduler

reservation_email = u'test@example.com'


class TestScheduler(IntegrationTestCase):

    @serialized
    def test_reserve(self):
        sc = Scheduler(new_uuid())

        start = datetime(2011, 1, 1, 15)
        end = datetime(2011, 1, 1, 16)

        allocations = sc.allocate(
            (start, end), raster=15, partly_available=True
        )

        self.assertEqual(1, len(allocations))

        allocation = allocations[0]

        # Add a second allocation in another scheduler, to ensure that
        # nothing bleeds over
        another = Scheduler(new_uuid())
        another.allocate((start, end))

        # 1 hour / 15 min = 4
        possible_dates = list(allocation.all_slots())
        self.assertEqual(len(possible_dates), 4)

        # reserve half of the slots
        time = (datetime(2011, 1, 1, 15), datetime(2011, 1, 1, 15, 30))
        token = sc.reserve(reservation_email, time)
        slots = sc.approve_reservation(token)

        self.assertEqual(len(slots), 2)

        # check the remaining slots
        remaining = allocation.free_slots()
        self.assertEqual(len(remaining), 2)
        self.assertEqual(remaining, possible_dates[2:])

        reserved_slots = sc.reserved_slots_by_reservation(token).all()
        self.assertEqual(slots, reserved_slots)

        # try to illegally move the slot
        movefn = lambda: sc.move_allocation(
            allocation.id,
            datetime(2011, 1, 1, 15, 30),
            datetime(2011, 1, 1, 16),
            None
        )
        self.assertRaises(AffectedReservationError, movefn)

        remaining = allocation.free_slots()
        self.assertEqual(len(remaining), 2)

        # actually move the slot
        sc.move_allocation(
            allocation.id,
            datetime(2011, 1, 1, 15),
            datetime(2011, 1, 1, 15, 30),
            None
        )

        # there should be fewer slots now
        remaining = allocation.free_slots()
        self.assertEqual(len(remaining), 0)

        # remove the reservation
        sc.remove_reservation(token)

        remaining = allocation.free_slots()
        self.assertEqual(len(remaining), 2)

    @serialized
    def test_group_reserve(self):
        sc = Scheduler(new_uuid())

        dates = [
            (datetime(2013, 4, 6, 12, 0), datetime(2013, 4, 6, 16, 0)),
            (datetime(2013, 4, 7, 12, 0), datetime(2013, 4, 7, 16, 0))
        ]

        allocations = sc.allocate(
            dates, grouped=True, approve_manually=True, quota=3
        )

        self.assertEqual(len(allocations), 2)

        group = allocations[0].group

        # reserve the same thing three times, which should yield equal results

        def reserve():
            token = sc.reserve(u'test@example.com', group=group)
            reservation = sc.reservation_by_token(token).one()

            targets = reservation._target_allocations().all()
            self.assertEqual(len(targets), 2)

            sc.approve_reservation(token)

            targets = reservation._target_allocations().all()
            self.assertEqual(len(targets), 2)

        reserve()
        reserve()
        reserve()

    @serialized
    def test_session_expiration(self):
        sc = Scheduler(new_uuid())

        session_id = new_uuid()

        start, end = datetime(2013, 5, 1, 13, 0), datetime(2013, 5, 1, 14)

        sc.allocate(dates=(start, end), approve_manually=True)

        sc.reserve(u'test@example.com', (start, end), session_id=session_id)

        created = utils.utcnow()
        db.Session.query(db.Reservation).filter(
            db.Reservation.session_id == session_id
        ).update({'created': created, 'modified': None})

        expired = db.find_expired_reservation_sessions(expiration_date=created)
        self.assertEqual(len(expired), 0)

        expired = db.find_expired_reservation_sessions(
            expiration_date=created + timedelta(microseconds=1)
        )
        self.assertEqual(len(expired), 1)

        db.Session.query(db.Reservation).filter(
            db.Reservation.session_id == session_id
        ).update({
            'created': created,
            'modified': created + timedelta(microseconds=1)
        })

        expired = db.find_expired_reservation_sessions(
            expiration_date=created + timedelta(microseconds=1)
        )
        self.assertEqual(len(expired), 0)

        expired = db.find_expired_reservation_sessions(
            expiration_date=created + timedelta(microseconds=2)
        )
        self.assertEqual(len(expired), 1)

    @serialized
    def test_invalid_reservation(self):
        sc = Scheduler(new_uuid())

        # try to reserve aspot that doesn't exist
        astart = datetime(2012, 1, 1, 15, 0)
        aend = datetime(2012, 1, 1, 16, 0)
        adates = (astart, aend)

        rstart = datetime(2012, 2, 1, 15, 0)
        rend = datetime(2012, 2, 1, 16, 0)
        rdates = (rstart, rend)

        sc.allocate(dates=adates, approve_manually=True)

        self.assertRaises(
            InvalidReservationError, sc.reserve, reservation_email, rdates
        )

    @serialized
    def test_waitinglist(self):
        sc = Scheduler(new_uuid())

        start = datetime(2012, 2, 29, 15, 0)
        end = datetime(2012, 2, 29, 19, 0)
        dates = (start, end)

        # let's create an allocation with a waitinglist
        allocation = sc.allocate(dates, approve_manually=True)[0]
        self.assertEqual(allocation.waitinglist_length, 0)

        # reservation should work
        approval_token = sc.reserve(reservation_email, dates)
        self.assertFalse(
            sc.reservation_by_token(approval_token).one().autoapprovable
        )
        self.assertTrue(allocation.is_available(start, end))
        self.assertEqual(allocation.waitinglist_length, 1)

        # as well as it's approval
        sc.approve_reservation(approval_token)
        self.assertFalse(allocation.is_available(start, end))
        self.assertEqual(allocation.waitinglist_length, 0)

        # at this point we can only reserve, not approve
        waiting_token = sc.reserve(reservation_email, dates)
        self.assertRaises(
            AlreadyReservedError, sc.approve_reservation, waiting_token
        )

        self.assertEqual(allocation.waitinglist_length, 1)

        # try to illegally move the allocation now
        self.assertRaises(
            AffectedReservationError, sc.move_allocation,
            allocation.id, start + timedelta(days=1), end + timedelta(days=1)
        )

        # we may now get rid of the existing approved reservation
        sc.remove_reservation(approval_token)
        self.assertEqual(allocation.waitinglist_length, 1)

        # which should allow us to approve the reservation in the waiting list
        sc.approve_reservation(waiting_token)
        self.assertEqual(allocation.waitinglist_length, 0)

    @serialized
    def test_no_bleed(self):
        """ Ensures that two allocations close to each other are not mistaken
        when using scheduler.reserve. If they do then they bleed over, hence
        the name.

        """
        sc = Scheduler(new_uuid())

        d1 = (datetime(2011, 1, 1, 15, 0), datetime(2011, 1, 1, 16, 0))
        d2 = (datetime(2011, 1, 1, 16, 0), datetime(2011, 1, 1, 17, 0))

        a1 = sc.allocate(d1)[0]
        a2 = sc.allocate(d2)[0]

        self.assertFalse(a1.overlaps(*d2))
        self.assertFalse(a2.overlaps(*d1))

        # expect no exceptions
        sc.reserve(reservation_email, d2)
        sc.reserve(reservation_email, d1)

    @serialized
    def test_waitinglist_group(self):
        from dateutil.rrule import rrule, DAILY, MO

        sc = Scheduler(new_uuid())
        days = list(rrule(
            DAILY, count=5, byweekday=(MO,), dtstart=datetime(2012, 1, 1)
        ))
        dates = []
        for d in days:
            dates.append(
                (
                    datetime(d.year, d.month, d.day, 15, 0),
                    datetime(d.year, d.month, d.day, 16, 0)
                )
            )

        allocations = sc.allocate(dates, grouped=True, approve_manually=True)
        self.assertEqual(len(allocations), 5)

        group = allocations[0].group

        # reserving groups is no different than single allocations
        maintoken = sc.reserve(reservation_email, group=group)
        self.assertFalse(
            sc.reservation_by_token(maintoken).one().autoapprovable
        )
        for allocation in allocations:
            self.assertEqual(allocation.waitinglist_length, 1)
        sc.approve_reservation(maintoken)

        token = sc.reserve(reservation_email, group=group)
        self.assertRaises(AlreadyReservedError, sc.approve_reservation, token)

        token = sc.reserve(reservation_email, group=group)
        self.assertRaises(AlreadyReservedError, sc.approve_reservation, token)

        sc.remove_reservation(maintoken)
        sc.approve_reservation(token)

    @serialized
    def test_group_move(self):
        sc = Scheduler(new_uuid())

        dates = [
            (datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0)),
            (datetime(2013, 1, 2, 12, 0), datetime(2013, 1, 2, 13, 0))
        ]

        allocations = sc.allocate(
            dates, grouped=True, quota=3,
            approve_manually=True, reservation_quota_limit=3
        )

        for allocation in allocations:
            self.assertEqual(len(allocation.siblings()), 3)

        self.assertEqual(allocations[0].group, allocations[1].group)

        # it is possible to move one allocation of a group, but all properties
        # but the date should remain the same

        newstart, newend = (
            datetime(2014, 1, 1, 12, 0), datetime(2014, 1, 1, 13, 0)
        )
        sc.move_allocation(
            allocations[0].id, newstart, newend,
            new_quota=2, approve_manually=True, reservation_quota_limit=2
        )

        group_allocations = sc.allocations_by_group(allocations[0].group).all()
        self.assertEqual(len(group_allocations), 2)

        for a in group_allocations:
            self.assertTrue(a.is_master)
            self.assertEqual(a.quota, 2)
            self.assertEqual(a.reservation_quota_limit, 2)

            for allocation in a.siblings():
                self.assertEqual(len(allocation.siblings()), 2)

        token = sc.reserve(u'test@example.com', group=allocations[0].group)
        sc.approve_reservation(token)

        group_allocations = sc.allocations_by_group(allocations[0].group).all()
        self.assertEqual(len(group_allocations), 2)
        all = utils.flatten([a.siblings() for a in group_allocations])
        self.assertEqual(db.availability_by_allocations(all), 50.0)

        sc.move_allocation(allocations[0].id, newstart, newend, new_quota=1)

        group_allocations = sc.allocations_by_group(allocations[0].group).all()
        all = list(utils.flatten([a.siblings() for a in group_allocations]))
        self.assertEqual(db.availability_by_allocations(all), 0.0)

        sc.move_allocation(allocations[0].id, newstart, newend, new_quota=2)

        token = sc.reserve(u'test@example.com', group=allocations[0].group)
        sc.approve_reservation(token)

        group_allocations = sc.allocations_by_group(allocations[0].group).all()
        all = list(utils.flatten([a.siblings() for a in group_allocations]))
        self.assertEqual(db.availability_by_allocations(all), 0.0)

        for a in all:
            self.assertFalse(a.is_available())

        self.assertEqual(len(all), 4)

        self.assertRaises(
            AffectedReservationError,
            sc.move_allocation,
            allocations[0].id, newstart, newend, None, 1
        )

    @serialized
    def test_no_waitinglist(self):
        sc = Scheduler(new_uuid())

        start = datetime(2012, 4, 6, 22, 0)
        end = datetime(2012, 4, 6, 23, 0)
        dates = (start, end)

        allocation = sc.allocate(dates, approve_manually=False)[0]

        self.assertEqual(allocation.waitinglist_length, 0)

        # the first reservation kinda gets us in a waiting list, though
        # this time there can be only one spot in the list as long as there's
        # no reservation

        token = sc.reserve(reservation_email, dates)
        self.assertTrue(sc.reservation_by_token(token).one().autoapprovable)
        sc.approve_reservation(token)

        # it is now that we should have a problem reserving
        self.assertRaises(
            AlreadyReservedError, sc.reserve, reservation_email, dates
        )
        self.assertEqual(allocation.waitinglist_length, 0)

        # until we delete the existing reservation
        sc.remove_reservation(token)
        sc.reserve(reservation_email, dates)

    @serialized
    def test_quota_waitinglist(self):
        sc = Scheduler(new_uuid())

        start = datetime(2012, 3, 4, 2, 0)
        end = datetime(2012, 3, 4, 3, 0)
        dates = (start, end)

        # in this example the waiting list will kick in only after
        # the quota has been filled

        allocation = sc.allocate(dates, quota=2, approve_manually=True)[0]
        self.assertEqual(allocation.waitinglist_length, 0)

        t1 = sc.reserve(reservation_email, dates)
        t2 = sc.reserve(reservation_email, dates)

        self.assertEqual(allocation.waitinglist_length, 2)

        sc.approve_reservation(t1)
        sc.approve_reservation(t2)

        self.assertEqual(allocation.waitinglist_length, 0)

        t3 = sc.reserve(reservation_email, dates)
        t4 = sc.reserve(reservation_email, dates)

        self.assertEqual(allocation.waitinglist_length, 2)

        self.assertRaises(AlreadyReservedError, sc.approve_reservation, t3)
        self.assertRaises(AlreadyReservedError, sc.approve_reservation, t4)

    def test_userlimits(self):
        # ensure that no user can make a reservation for more than 24 hours at
        # the time. the user acutally can't do that anyway, since we do not
        # offer start / end dates, but a day and two times. But if this changes
        # in the future it should throw en error first, because it would mean
        # that we have to look at how to stop the user from reserving one year
        # with a single form.

        start = datetime(2011, 1, 1, 15, 0)
        end = start + timedelta(days=1)

        sc = Scheduler(new_uuid())

        self.assertRaises(
            ReservationTooLong, sc.reserve, reservation_email, (start, end)
        )

    def test_allocation_overlap(self):
        sc1 = Scheduler(new_uuid())
        sc2 = Scheduler(new_uuid())

        start = datetime(2011, 1, 1, 15, 0)
        end = datetime(2011, 1, 1, 16, 0)

        sc1.allocate((start, end), raster=15)
        sc2.allocate((start, end), raster=15)

        self.assertRaises(
            OverlappingAllocationError, sc1.allocate, (start, end), raster=15
        )

        # there's another way this could happen, which is illegal usage
        # of scheduler.allocate - we stop this befor it hits the database
        sc = Scheduler(new_uuid())

        dates = [
            (datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0)),
            (datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0))
        ]

        self.assertRaises(InvalidAllocationError, sc.allocate, dates)

        dates = [
            (datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0)),
            (datetime(2013, 1, 1, 13, 0), datetime(2013, 1, 1, 14, 0))
        ]

        self.assertRaises(InvalidAllocationError, sc.allocate, dates)

        dates = [
            (datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0)),
            (datetime(2013, 1, 1, 13, 15), datetime(2013, 1, 1, 14, 0))
        ]

        sc.allocate(dates)

    def test_allocation_partition(self):
        sc = Scheduler(new_uuid())

        allocations = sc.allocate(
            (
                datetime(2011, 1, 1, 8, 0),
                datetime(2011, 1, 1, 10, 0)
            ),
            partly_available=True
        )

        allocation = allocations[0]
        partitions = allocation.availability_partitions()
        self.assertEqual(len(partitions), 1)
        self.assertEqual(partitions[0][0], 100.0)
        self.assertEqual(partitions[0][1], False)

        start, end = datetime(2011, 1, 1, 8, 30), datetime(2011, 1, 1, 9, 00)

        token = sc.reserve(reservation_email, (start, end))
        sc.approve_reservation(token)

        partitions = allocation.availability_partitions()
        self.assertEqual(len(partitions), 3)
        self.assertEqual(partitions[0][0], 25.00)
        self.assertEqual(partitions[0][1], False)
        self.assertEqual(partitions[1][0], 25.00)
        self.assertEqual(partitions[1][1], True)
        self.assertEqual(partitions[2][0], 50.00)
        self.assertEqual(partitions[2][1], False)

    def test_partly(self):
        sc = Scheduler(new_uuid())

        allocations = sc.allocate(
            (
                datetime(2011, 1, 1, 8, 0),
                datetime(2011, 1, 1, 18, 0)
            ),
            partly_available=False,
            approve_manually=False
        )

        self.assertEqual(1, len(allocations))
        allocation = allocations[0]

        self.assertEqual(1, len(list(allocation.all_slots())))
        self.assertEqual(1, len(list(allocation.free_slots())))

        slot = list(allocation.all_slots())[0]
        self.assertEqual(slot[0], allocation.start)
        self.assertEqual(slot[1], allocation.end)

        slot = list(allocation.free_slots())[0]
        self.assertEqual(slot[0], allocation.start)
        self.assertEqual(slot[1], allocation.end)

        token = sc.reserve(
            reservation_email,
            (datetime(2011, 1, 1, 16, 0), datetime(2011, 1, 1, 18, 0))
        )
        sc.approve_reservation(token)
        self.assertRaises(
            AlreadyReservedError, sc.reserve, reservation_email,
            (datetime(2011, 1, 1, 8, 0), datetime(2011, 1, 1, 9, 0))
        )

    @serialized
    def test_quotas(self):
        sc = Scheduler(new_uuid())

        start = datetime(2011, 1, 1, 15, 0)
        end = datetime(2011, 1, 1, 16, 0)

        # setup an allocation with ten spots
        allocations = sc.allocate(
            (start, end), raster=15, quota=10, approve_manually=False
        )
        allocation = allocations[0]

        # which should give us ten allocations (-1 as the master is not
        # counted)
        self.assertEqual(9, len(sc.allocation_mirrors_by_master(allocation)))

        # the same reservation can now be made ten times
        for i in range(0, 10):
            sc.approve_reservation(sc.reserve(reservation_email, (start, end)))

        # the 11th time it'll fail
        self.assertRaises(
            AlreadyReservedError, sc.reserve, reservation_email, [(start, end)]
        )
        other = Scheduler(new_uuid())

        # setup an allocation with five spots
        allocations = other.allocate(
            [(start, end)], raster=15, quota=5, partly_available=True,
            approve_manually=False
        )
        allocation = allocations[0]

        self.assertEqual(
            4, len(other.allocation_mirrors_by_master(allocation))
        )

        # we can do ten reservations if every reservation only occupies half
        # of the allocation
        for i in range(0, 5):
            other.approve_reservation(
                other.reserve(
                    reservation_email,
                    (datetime(2011, 1, 1, 15, 0), datetime(2011, 1, 1, 15, 30))
                )
            )
            other.approve_reservation(
                other.reserve(
                    reservation_email,
                    (datetime(2011, 1, 1, 15, 30), datetime(2011, 1, 1, 16, 0))
                )
            )

        self.assertRaises(
            AlreadyReservedError, other.reserve, reservation_email,
            ((datetime(2011, 1, 1, 15, 30), datetime(2011, 1, 1, 16, 0)))
        )

        # test some queries
        allocations = sc.allocations_in_range(start, end)
        self.assertEqual(1, allocations.count())

        allocations = other.allocations_in_range(start, end)
        self.assertEqual(1, allocations.count())

        allocation = sc.allocation_by_date(start, end)
        sc.allocation_by_id(allocation.id)
        self.assertEqual(9, len(sc.allocation_mirrors_by_master(allocation)))

        allocation = other.allocation_by_date(start, end)
        other.allocation_by_id(allocation.id)
        self.assertEqual(
            4, len(other.allocation_mirrors_by_master(allocation))
        )

    def test_fragmentation(self):
        sc = Scheduler(new_uuid())

        start = datetime(2011, 1, 1, 15, 0)
        end = datetime(2011, 1, 1, 16, 0)
        daterange = (start, end)

        allocation = sc.allocate(daterange, quota=3)[0]

        reservation = sc.reserve(reservation_email, daterange)
        slots = sc.approve_reservation(reservation)
        self.assertTrue([True for s in slots if s.resource == sc.uuid])

        slots = sc.approve_reservation(
            sc.reserve(reservation_email, daterange)
        )
        self.assertFalse([False for s in slots if s.resource == sc.uuid])

        sc.remove_reservation(reservation)

        slots = sc.approve_reservation(
            sc.reserve(reservation_email, daterange)
        )
        self.assertTrue([True for s in slots if s.resource == sc.uuid])

        self.assertRaises(
            AffectedReservationError, sc.remove_allocation, allocation.id
        )

    @serialized
    def test_imaginary_mirrors(self):
        sc = Scheduler(new_uuid())

        start = datetime(2011, 1, 1, 15, 0)
        end = datetime(2011, 1, 1, 16, 0)
        daterange = (start, end)

        allocation = sc.allocate(daterange, quota=3)[0]
        self.assertTrue(allocation.is_master)

        mirrors = sc.allocation_mirrors_by_master(allocation)
        imaginary = len([m for m in mirrors if m.is_transient])
        self.assertEqual(imaginary, 2)
        self.assertEqual(len(allocation.siblings()), 3)

        masters = len([m for m in mirrors if m.is_master])
        self.assertEqual(masters, 0)
        self.assertEqual(
            len([s for s in allocation.siblings(imaginary=False)]), 1
        )

        sc.approve_reservation(sc.reserve(reservation_email, daterange))
        mirrors = sc.allocation_mirrors_by_master(allocation)
        imaginary = len([m for m in mirrors if m.is_transient])
        self.assertEqual(imaginary, 2)

        sc.approve_reservation(sc.reserve(reservation_email, daterange))
        mirrors = sc.allocation_mirrors_by_master(allocation)
        imaginary = len([m for m in mirrors if m.is_transient])
        self.assertEqual(imaginary, 1)

        sc.approve_reservation(sc.reserve(reservation_email, daterange))
        mirrors = sc.allocation_mirrors_by_master(allocation)
        imaginary = len([m for m in mirrors if m.is_transient])
        self.assertEqual(imaginary, 0)
        self.assertEqual(len(mirrors) + 1, len(allocation.siblings()))

    @serialized
    def test_quota_changes(self):
        sc = Scheduler(new_uuid())

        start = datetime(2011, 1, 1, 15, 0)
        end = datetime(2011, 1, 1, 16, 0)
        daterange = (start, end)

        master = sc.allocate(daterange, quota=5)[0]

        reservations = []
        for i in range(0, 5):
            reservations.append(sc.reserve(reservation_email, daterange))

        for r in reservations:
            sc.approve_reservation(r)

        mirrors = sc.allocation_mirrors_by_master(master)

        self.assertFalse(master.is_available())
        self.assertEqual(4, len([m for m in mirrors if not m.is_available()]))

        sc.remove_reservation(reservations[0])
        self.assertTrue(master.is_available())
        reservations = reservations[1:]

        # by removing the reservation on the master and changing the quota
        # a reordering is triggered which will ensure that the master and the
        # mirrors are reserved without gaps (master, mirror 0, mirror 1 usw..)
        # so we should see an unavailable master after changing the quota
        sc.change_quota(master, 4)
        self.assertFalse(master.is_available())
        self.assertEqual(4, master.quota)

        mirrors = sc.allocation_mirrors_by_master(master)
        self.assertEqual(3, len([m for m in mirrors if not m.is_available()]))

        for reservation in reservations:
            sc.remove_reservation(reservation)

        self.assertTrue(master.is_available())
        mirrors = sc.allocation_mirrors_by_master(master)
        self.assertEqual(0, len([m for m in mirrors if not m.is_available()]))

        # this is a good time to check if the siblings function from the
        # allocation acts the same on each mirror and master
        siblings = master.siblings()
        for s in siblings:
            self.assertEqual(s.siblings(), siblings)

        # let's do another round, adding 7 reservations and removing the three
        # in the middle, which should result in a reordering:
        # -> 1, 2, 3, 4, 5, 6, 7
        # -> 1, 2, -, -, 5, -, 7
        # => 1, 2, 3, 4, -, - ,-

        sc.change_quota(master, 7)

        sc.reserve(reservation_email, daterange)
        r2 = sc.reserve(reservation_email, daterange)
        r3 = sc.reserve(reservation_email, daterange)
        r4 = sc.reserve(reservation_email, daterange)
        r5 = sc.reserve(reservation_email, daterange)
        r6 = sc.reserve(reservation_email, daterange)
        r7 = sc.reserve(reservation_email, daterange)

        for r in [r2, r3, r4, r5, r6, r7]:
            sc.approve_reservation(r)

        a2 = sc.allocations_by_reservation(r2).one().id
        a3 = sc.allocations_by_reservation(r3).one().id
        a4 = sc.allocations_by_reservation(r4).one().id
        a5 = sc.allocations_by_reservation(r5).one().id
        a7 = sc.allocations_by_reservation(r7).one().id

        sc.remove_reservation(r3)
        sc.remove_reservation(r4)
        sc.remove_reservation(r6)

        sc.change_quota(master, 4)

        a2_ = sc.allocations_by_reservation(r2).one().id
        a5_ = sc.allocations_by_reservation(r5).one().id
        a7_ = sc.allocations_by_reservation(r7).one().id

        self.assertTrue(a2_ == a2)

        self.assertTrue(a5_ == a3)
        self.assertTrue(a5_ != a5)

        self.assertTrue(a7_ == a4)
        self.assertTrue(a7_ != a7)

    @serialized
    def test_availability(self):
        start = datetime(2011, 1, 1, 15, 0)
        end = datetime(2011, 1, 1, 16, 0)

        sc = Scheduler(new_uuid())
        a = sc.allocate((start, end), raster=15, partly_available=True)[0]

        sc.approve_reservation(
            sc.reserve(
                reservation_email,
                (datetime(2011, 1, 1, 15, 0), datetime(2011, 1, 1, 15, 15))
            )
        )

        self.assertEqual(a.availability, 75.0)
        self.assertEqual(a.availability, sc.availability())

        sc.approve_reservation(
            sc.reserve(
                reservation_email,
                (datetime(2011, 1, 1, 15, 45), datetime(2011, 1, 1, 16, 0))
            )
        )
        self.assertEqual(a.availability, 50.0)
        self.assertEqual(a.availability, sc.availability())

        sc.approve_reservation(
            sc.reserve(
                reservation_email,
                (datetime(2011, 1, 1, 15, 15), datetime(2011, 1, 1, 15, 30))
            )
        )
        self.assertEqual(a.availability, 25.0)
        self.assertEqual(a.availability, sc.availability())

        sc.approve_reservation(
            sc.reserve(
                reservation_email,
                (datetime(2011, 1, 1, 15, 30), datetime(2011, 1, 1, 15, 45))
            )
        )
        self.assertEqual(a.availability, 0.0)
        self.assertEqual(a.availability, sc.availability())

        sc = Scheduler(new_uuid())

        a = sc.allocate((start, end), quota=4)[0]

        self.assertEqual(a.availability, 100.0)  # master only!

        sc.approve_reservation(
            sc.reserve(reservation_email, (start, end))
        )

        self.assertEqual(75.0, sc.availability())

        self.assertEqual(a.availability, 0.0)  # master only!

        sc.approve_reservation(
            sc.reserve(reservation_email, (start, end))
        )
        self.assertEqual(50.0, sc.availability())

        sc.approve_reservation(
            sc.reserve(reservation_email, (start, end))
        )
        self.assertEqual(25.0, sc.availability())

        sc.approve_reservation(
            sc.reserve(reservation_email, (start, end))
        )
        self.assertEqual(0.0, sc.availability())

    @serialized
    def test_events(self):

        # hookup test event subscribers
        reservation_made_event = self.subscribe(events.ReservationMadeEvent)
        reservation_approved_event = self.subscribe(
            events.ReservationApprovedEvent
        )
        reservation_denied_event = self.subscribe(
            events.ReservationDeniedEvent
        )
        reservation_revoked_event = self.subscribe(
            events.ReservationRevokedEvent
        )

        self.assertFalse(reservation_made_event.was_fired())
        self.assertFalse(reservation_approved_event.was_fired())
        self.assertFalse(reservation_denied_event.was_fired())
        self.assertFalse(reservation_revoked_event.was_fired())

        # prepare reservation
        sc = Scheduler(new_uuid())

        start = datetime(2012, 2, 29, 15, 0)
        end = datetime(2012, 2, 29, 19, 0)
        dates = (start, end)

        # do reservation
        start = datetime(2012, 1, 1, 15, 0)
        end = datetime(2012, 1, 1, 19, 0)
        dates = (start, end)

        sc.allocate(dates, approve_manually=True)
        token = sc.reserve(reservation_email, dates)

        self.assertTrue(reservation_made_event.was_fired())
        self.assertEqual(reservation_made_event.event.reservation.token, token)

        reservation_made_event.reset()

        # approve it
        sc.approve_reservation(token)

        self.assertTrue(reservation_approved_event.was_fired())
        self.assertFalse(reservation_denied_event.was_fired())
        self.assertFalse(reservation_made_event.was_fired())

        self.assertEqual(
            reservation_approved_event.event.reservation.token, token
        )

        reservation_approved_event.reset()
        reservation_denied_event.reset()

        # revoke the reservation and deny the next one
        sc.revoke_reservation(token, u'no-reason')

        self.assertTrue(reservation_revoked_event.was_fired())

        token = sc.reserve(reservation_email, dates)

        self.assertTrue(reservation_made_event.was_fired())

        sc.deny_reservation(token)

        self.assertFalse(reservation_approved_event.was_fired())
        self.assertTrue(reservation_denied_event.was_fired())

        self.assertEqual(
            reservation_denied_event.event.reservation.token, token
        )

    @serialized
    def test_email(self):
        self.login_manager()

        mail = self.mailhost
        resource = self.create_resource()
        sc = resource.scheduler()

        start = datetime(2012, 2, 29, 15, 0)
        end = datetime(2012, 2, 29, 19, 0)
        dates = (start, end)

        datestr = start.strftime('%d.%m.%Y %H:%M - ') + end.strftime('%H:%M')

        data = utils.mock_data_dictionary(
            {
                'name': u'Björn',
                'icanhazcharacter': '%s'
            }
        )

        def assert_data_in_mail(message, assert_as=True):
            self.assertEqual('name' in message, assert_as)
            self.assertEqual('Bj=C3=B6rn' in message, assert_as)
            self.assertEqual('icanhazcharacter' in message, assert_as)
            self.assertEqual('%s' in message, assert_as)

            # the date should always be there
            self.assertTrue(datestr in message)

        # do an unapproved reservation
        start = datetime(2012, 2, 29, 15, 0)
        end = datetime(2012, 2, 29, 19, 0)
        dates = (start, end)

        # one email is sent because we do not have a manager yet
        session_id = new_uuid()

        allocation = sc.allocate(dates, approve_manually=False)[0]
        token = sc.reserve(
            reservation_email,
            dates, data=data, session_id=session_id
        )
        sc.confirm_reservations_for_session(session_id)

        self.assertEqual(len(mail.messages), 1)
        self.assertTrue('Your Reservations' in mail.messages[0])
        self.assertTrue(resource.title in mail.messages[0])
        self.assertTrue(reservation_email in mail.messages[0])

        # autoapproved reservations do not have a star
        self.assertFalse('* {}'.format(resource.title) in mail.messages[0])

        # the mail sending happens before the (automatic) approval,
        # so there should be no change after
        sc.approve_reservation(token)

        self.assertEqual(len(mail.messages), 1)
        mail.messages = []

        # there is an email again when the reservation is revoked
        sc.revoke_reservation(token, u'no-reason')
        self.assertEqual(len(mail.messages), 1)
        self.assertTrue(u'no-reason' in mail.messages[0])
        mail.messages = []

        sc.remove_allocation(allocation.id)

        # make multiple reservations in one session to different email
        # recipients. this should yield multiple mails
        allocation = sc.allocate(dates, approve_manually=False, quota=3)[0]

        tokens = (
            sc.reserve(
                u'one@example.com', dates, data=data, session_id=session_id
            ),
            sc.reserve(
                u'one@example.com', dates, data=data, session_id=session_id
            ),
            sc.reserve(
                u'two@example.com',
                dates, data=data, session_id=session_id
            )
        )
        sc.confirm_reservations_for_session(session_id)
        map(sc.deny_reservation, tokens)

        self.assertEqual(len(mail.messages), 2)
        self.assertTrue('one@example.com' in mail.messages[0])
        self.assertFalse('two@example.com' in mail.messages[0])
        self.assertFalse('one@example.com' in mail.messages[1])
        self.assertTrue('two@example.com' in mail.messages[1])

        sc.remove_allocation(allocation.id)
        mail.messages = []

        # now let's try with an approved reservation
        allocation = sc.allocate(dates, approve_manually=True)[0]
        token = sc.reserve(
            reservation_email,
            dates, data=data, session_id=session_id
        )
        sc.confirm_reservations_for_session(session_id)

        # no manager is defined, so we expect to have one email to the reservee
        self.assertEqual(len(mail.messages), 1)
        self.assertTrue('Your Reservations' in mail.messages[0])
        self.assertTrue(reservation_email in mail.messages[0])

        # reservations which require approval have a star
        self.assertTrue('* {}'.format(resource.title) in mail.messages[0])

        # let's decline that one
        sc.deny_reservation(token)
        self.assertEqual(len(mail.messages), 2)
        self.assertTrue('Denied' in mail.messages[1])
        self.assertTrue(reservation_email in mail.messages[0])
        assert_data_in_mail(mail.messages[1], False)  # no data here

        # add a manager to the resource and start anew
        self.assign_reservation_manager('manager@example.com', resource)
        mail.messages = []

        token = sc.reserve(
            reservation_email,
            dates, data=data, session_id=session_id
        )
        sc.confirm_reservations_for_session(session_id)
        self.assertEqual(len(mail.messages), 2)

        # the first email is the one sent to the reservee
        self.assertTrue('Your Reservations' in mail.messages[0])
        self.assertTrue(reservation_email in mail.messages[0])

        # the second is the on sent to the manager
        self.assertTrue('New Reservation' in mail.messages[1])
        self.assertTrue('To approve' in mail.messages[1])
        self.assertTrue('To deny' in mail.messages[1])
        self.assertTrue(reservation_email in mail.messages[1])
        self.assertTrue(str(token) in mail.messages[1])
        assert_data_in_mail(mail.messages[1])

        # approval results in the last mail
        sc.approve_reservation(token)

        self.assertEqual(len(mail.messages), 3)
        self.assertTrue('Reservation for' in mail.messages[2])
        self.assertTrue(reservation_email in mail.messages[2])

        sc.remove_reservation(token)
        sc.remove_allocation(allocation.id)
        mail.messages = []

        # try an auto approved allocation again, this time we get two emails
        # because there's a manager
        session_id = new_uuid()
        allocation = sc.allocate(dates, approve_manually=False)[0]
        token = sc.reserve(
            reservation_email,
            dates, data=data, session_id=session_id
        )
        sc.confirm_reservations_for_session(session_id)

        self.assertEqual(len(mail.messages), 2)

        # the reservee mail is sent first
        self.assertTrue('Your Reservations' in mail.messages[0])
        self.assertTrue(reservation_email in mail.messages[0])

        # the second is the one sent to the manager
        self.assertTrue('New Reservation' in mail.messages[1])
        self.assertFalse('To approve' in mail.messages[1])
        self.assertFalse('To deny' in mail.messages[1])
        self.assertTrue('To cancel' in mail.messages[1])
        self.assertTrue(reservation_email in mail.messages[1])
        self.assertTrue(str(token) in mail.messages[1])
        assert_data_in_mail(mail.messages[1])
