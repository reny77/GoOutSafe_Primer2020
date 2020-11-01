"""
This test case covered all simple action that we can do from the UI
"""

import pytest
from utils import (
    login,
    logout,
    register_user,
    get_user_with_email,
    register_restaurant,
    get_rest_with_name,
    get_rest_with_name_and_phone,
)
from monolith.database import db, User, Restaurant, Positive, Review, Reservation, RestaurantTable, OpeningHours
from monolith.forms import (
    UserForm,
    RestaurantForm,
    SearchUserForm,
    ReviewForm,
    DishForm,
    ReservationForm, PhotoGalleryForm,
)
from monolith.tests.utils import (
    visit_restaurant,
    visit_photo_gallery,
    mark_people_for_covid19,
    visit_reservation,
    make_revew,
    delete_positive_with_user_id,
    del_user_on_db,
    unmark_people_for_covid19,
    search_contact_positive_covid19,
    create_new_menu,
    create_new_reservation, create_new_user_with_form, create_new_restaurant_with_form, create_new_table,
    create_new_photo,
)

import datetime


@pytest.mark.usefixtures("client")
class Test_GoOutSafeForm:
    def test_login_form_ok(self, client):
        """
        This test suit test the operation that we can do
        to login correctly an user
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        q = db.session.query(User).filter_by(email=email)
        q_user = q.first()
        assert q_user is not None
        assert q_user.authenticate(password) is True

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

        q = db.session.query(User).filter_by(email=email)
        q_user = q.first()
        assert q_user is not None

    def test_login_form_ko(self, client):
        """
        This test suit test the operation that we can do
        to login correctly an user
        """
        email = "vincenzopalazzo@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "error_login" in response.data.decode("utf-8")

        q = db.session.query(User).filter_by(email=email)
        q_user = q.first()
        assert q_user is None

    def test_register_new_user_ok(self, client):
        """
        This use case try to login a new user with a correct execution

        The flow of this test is
        - Create user
        - Verify user on db
        - login user
        - verify the html returned from flask
        :param client: The flask app created inside the fixtures
        """
        user_form = UserForm()
        user_form.email = "Trumps_doctor@usa.gov"
        user_form.firstname = "Anthony"
        user_form.lastname = "Fauci"
        user_form.dateofbirth = "12/12/2020"
        user_form.password = "nocovid_in_us"
        response = register_user(client, user_form)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        ## Search inside the DB if this user exist
        user_query = get_user_with_email(user_form.email)
        assert user_query is not None
        assert user_query.authenticate(user_form.password) is True

        response = login(client, user_form.email, user_form.password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = logout(client)
        assert response.status_code == 200
        assert "anonymous_test" not in response.data.decode("utf-8")

        db.session.query(User).filter_by(id=user_query.id).delete()
        db.session.commit()

    def test_modify_user(self, client):
        pass

    def test_register_new_restaurant_ko(self, client):
        """
        This test test the use case to create a new restaurant
        and this test have the follow described below

        - Login like a operator (user the standard account)
        - Register a new restaurant
        - Look inside the db  to see if the restaurant exist
        - Log out user
        - See if the restaurant is present on home screen.

        :param client:
        """
        email = "ham.burger@email.com"
        password = "operator"
        login(client, email, password)
        restaurant_form = RestaurantForm()
        restaurant_form.name = "Gino Sorbillo"
        restaurant_form.phone = "096321343"
        restaurant_form.lat = 12
        restaurant_form.lon = 12
        restaurant_form.n_tables = 50
        restaurant_form.covid_measures = "We can survive"
        restaurant_form.cuisine = "0"
        restaurant_form.open_days = "0"
        restaurant_form.open_lunch = "12:00"
        restaurant_form.close_lunch = "15:00"
        restaurant_form.open_dinner = "18:00"
        restaurant_form.close_dinner = "00:00"
        response = register_restaurant(client, restaurant_form)
        assert response.status_code == 200  ## Regirect to /
        assert restaurant_form.name in response.data.decode("utf-8")
        assert "logged_test" in response.data.decode("utf-8")
        rest = get_rest_with_name(restaurant_form.name)
        assert rest is not None
        response = logout(client)
        assert response.status_code == 200
        response = client.get("/")  ## get index
        assert restaurant_form.name in response.data.decode("utf-8")

        db.session.query(rest.id).delete()
        db.session.commit()

    def test_register_new_restaurant_ko(self, client):
        """
        This test test the use case to create a new restaurant but the user
        and this test have the follow described below

        - Register a new user
        - Register a new restaurant
        - receive the 401 error because the user is not a customer
        - Delete the user

        :param client:
        """
        email = "alibaba@gmail.com"
        password = "alibaba"
        user_form = UserForm()
        user_form.email = email
        user_form.firstname = "alibaba"
        user_form.lastname = "alibaba"
        user_form.dateofbirth = "12/12/2020"
        user_form.password = password
        response = register_user(client, user_form)
        assert response.status_code == 200
        response = login(client, user_form.email, user_form.password)
        assert "logged_test" in response.data.decode("utf-8")

        user = get_user_with_email(user_form.email)
        assert user is not None
        assert user.role_id == 3  ## Customer

        # login(client, email, password)
        restaurant_form = RestaurantForm()
        restaurant_form.name = "Gino Sorbillo"
        restaurant_form.phone = "096321343"
        restaurant_form.lat = 12
        restaurant_form.lon = 12
        restaurant_form.n_tables = 50
        restaurant_form.covid_measures = "We can survive"
        restaurant_form.cuisine = ["Italian food"]
        restaurant_form.open_days = ["0"]
        restaurant_form.open_lunch = "12:00"
        restaurant_form.close_lunch = "15:00"
        restaurant_form.open_dinner = "18:00"
        restaurant_form.close_dinner = "00:00"
        response = register_restaurant(client, restaurant_form)
        assert response.status_code == 401
        rest = get_rest_with_name(restaurant_form.name)
        assert rest is None

        db.session.query(User).filter_by(id=user.id).delete()
        db.session.commit()

    def test_modify_new_restaurant(self, client):
        pass

    def test_research_restaurant_by_name(self, client):
        pass

    def test_open_photo_view_ok(self, client):
        """
        This test perform the use case described below
        - create a new user
        - create a new restaurant
        - open the single restaurant view
        - Go to photo gallery
        - check if the page is load correctly
        """
        user = UserForm()
        user.email = "cr7@gmail.com"
        user.firstname = "Cristiano"
        user.lastname = "Ronaldo"
        user.password = "Siii"
        user.dateofbirth = "12/12/1975"
        register_user(client, user)
        response = login(client, user.email, user.password)
        assert response is not None
        assert "logged_test" in response.data.decode("utf-8")

        restaurant = db.session.query(Restaurant).all()[0]
        response = visit_restaurant(client, restaurant.id)
        assert response.status_code == 200
        assert "visit_rest_test" in response.data.decode("utf-8")

        user_stored = get_user_with_email(user.email)
        response = visit_photo_gallery(client)
        ## the user is a customer and not a operator
        assert response.status_code == 401

        db.session.query(User).filter_by(id=user_stored.id).delete()
        db.session.commit()

    def test_mark_positive_ko(self, client):
        """
        This test cases test the use case to mark a person as covid19
        positive, the work flow is the following:
        - Login as normal user (this is wrong, the test should be failed)
        - Create a new customer
        - mark this customer as positive
        - delete the customer
        :param client:
        """
        response = login(client, "john.doe@email.com", "customer")
        assert response.status_code == 200

        user = UserForm()
        user.email = "messi@gmail.com"
        user.firstname = "Messi"
        user.lastname = "Ronaldo"
        user.password = "messi"
        user.phone = "32455"
        user.dateofbirth = "12/12/1975"
        register_user(client, user)

        mark = SearchUserForm()
        mark.email = user.email
        mark.phone = user.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 401

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )

        assert q_already_positive is None

        delete_positive_with_user_id(q_user.id)
        del_user_on_db(q_user.id)

    def test_mark_positive_ok(self, client):
        """
        This test cases test the use case to mark a person as covid19
        positive, the work flow is the following:
        - Login as normal user (this is wrong, the test should be failed)
        - Create a new customer
        - mark this customer as positive
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email = "cr7@gmail.com"
        user.firstname = "Cristiano"
        user.lastname = "Ronaldo"
        user.password = "Siii"
        user.phone = "1234555"
        user.dateofbirth = "12/12/1975"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = user.email
        mark.phone = user.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )
        assert q_already_positive is not None

        delete_positive_with_user_id(q_user.id)
        del_user_on_db(q_user.id)

    def test_see_reservation_ko(self, client):
        """
        This test test the
        """
        email = "health_authority@gov.com"
        pazz = "nocovid"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = visit_reservation(
            client, from_date="2013-10-07", to_date="2014-10-07", email=email
        )
        assert response.status_code == 401

    def test_see_reservation_ok(self, client):
        """
        This test test the use case to perform the request to access from reservation
        as customer
        """
        email = "ham.burger@email.com"
        pazz = "operator"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = visit_reservation(
            client, from_date="2013-10-07", to_date="2014-10-07", email=email
        )
        assert response.status_code == 200
        assert "restaurant_reservations_test" in response.data.decode("utf-8")

    def test_make_review_ko(self, client):
        """
        TODO
        """
        email = "health_authority@gov.com"
        pazz = "nocovid"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        trial_rest = db.session.query(Restaurant).all()[0]
        form = ReviewForm()
        form.stars = 3
        form.review = "Good food"
        response = make_revew(client, trial_rest.id, form)
        assert response.status_code == 401

    def test_make_review_ok(self, client):
        """
        TODO
        """
        email = "ham.burger@email.com"
        pazz = "operator"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        trial_rest = db.session.query(Restaurant).all()[0]
        form = ReviewForm()
        form.stars = 3
        form.review = "Good food"
        response = make_revew(client, trial_rest.id, form)
        assert response.status_code == 200
        assert "review_done_test" in response.data.decode("utf-8")

        db.session.query(Review).filter_by(review=form.review).delete()
        db.session.commit()

    def test_mark_positive_ko_user_already_positive(self, client):
        user = UserForm()
        user.email = "joe@gmail.com"
        user.firstname = "joe"
        user.lastname = "joe"
        user.password = "joejoe"
        user.phone = "324545"
        user.dateofbirth = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = user.email
        mark.phone = user.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )
        assert q_already_positive is not None

        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )
        assert q_already_positive is not None

        delete_positive_with_user_id(q_user.id)
        del_user_on_db(q_user.id)

    def test_mark_positive_ko_not_registered_user(self, client):
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = "joe@gmail.com"
        mark.phone = "324545"
        response = unmark_people_for_covid19(client, mark)
        assert response.status_code == 200

    def test_mark_positive_ko_empty_fields(self, client):
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = ""
        mark.phone = ""
        response = unmark_people_for_covid19(client, mark)
        assert response.status_code == 200

    def test_unmark_positive_ko_unathorized(self, client):
        response = login(client, "john.doe@email.com", "customer")
        assert response.status_code == 200

        user = UserForm()
        user.email = "joe@gmail.com"
        user.firstname = "joe"
        user.lastname = "joe"
        user.password = "joejoe"
        user.phone = "324545"
        user.dateofbirth = "24/10/1987"
        register_user(client, user)

        unmark = SearchUserForm()
        unmark.email = user.email
        unmark.phone = user.phone
        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 401

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )

        assert q_already_positive is None

        del_user_on_db(q_user.id)

    def test_unmark_positive_ko_user_not_positive(self, client):
        user = UserForm()
        user.email = "joe@gmail.com"
        user.firstname = "joe"
        user.lastname = "joe"
        user.password = "joejoe"
        user.phone = "324545"
        user.dateofbirth = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        unmark = SearchUserForm()
        unmark.email = user.email
        unmark.phone = user.phone
        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )

        assert q_already_positive is None

        del_user_on_db(q_user.id)

    def test_unmark_positive_ko_user_not_registered(self, client):
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        unmark = SearchUserForm()
        unmark.email = "joe@gmail.com"
        unmark.phone = "324545"
        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 200

    def test_unmark_positive_ko_empty_fields(self, client):
        user = UserForm()
        user.email = "joe@gmail.com"
        user.firstname = "joe"
        user.lastname = "joe"
        user.password = "joejoe"
        user.phone = "324545"
        user.dateofbirth = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = user.email
        mark.phone = user.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )
        assert q_already_positive is not None

        unmark = SearchUserForm()
        unmark.email = ""
        unmark.phone = ""

        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )
        assert q_already_positive is not None

        delete_positive_with_user_id(q_user.id)
        del_user_on_db(q_user.id)

    def test_unmark_positive_ok(self, client):
        user = UserForm()
        user.email = "joe@gmail.com"
        user.firstname = "joe"
        user.lastname = "joe"
        user.password = "joejoe"
        user.phone = "324545"
        user.dateofbirth = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = user.email
        mark.phone = user.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )
        assert q_already_positive is not None

        response = unmark_people_for_covid19(client, mark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )
        assert q_already_positive is None

        delete_positive_with_user_id(q_user.id)
        del_user_on_db(q_user.id)

    def test_search_contacts_with_positive_ko(self, client):
        user = UserForm()
        user.email = "joe@gmail.com"
        user.firstname = "joe"
        user.lastname = "joe"
        user.password = "joejoe"
        user.phone = "324545"
        user.dateofbirth = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = user.email
        mark.phone = user.phone
        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200

        q_user = get_user_with_email(user.email)
        del_user_on_db(q_user.id)

    def test_search_contacts_with_user_not_registered(self, client):
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email = "joe@gmail.com"
        mark.phone = "324545"
        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200

    def test_create_new_menu_restaurant_ok(self, client):
        """
        This test case perform the request with flask client to make
        the request to access at the db
        :param client:
        :return:
        """
        email = "ham.burger@email.com"
        pazz = "operator"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # GET
        response = client.get("/restaurant/menu")
        assert response.status_code is 200

        rest = db.session.query(Restaurant).all()[0]
        form = DishForm()
        form.name = "Pasta"
        form.price = 14
        with client.session_transaction() as session:
            session["RESTAURANT_ID"] = rest.id
        response = create_new_menu(client, form)
        assert response.status_code is 200
        assert "menu_ok_test" in response.data.decode("utf-8")

        logout(client)

    def test_create_new_menu_restaurant_ko(self, client):
        """
        This test case perform the request with flask client to make
        the request to access at the db
        :param client:
        :return:
        """
        rest = db.session.query(Restaurant).all()[0]
        form = DishForm()
        form.name = "Pasta"
        form.price = 14
        with client.session_transaction() as session:
            session["RESTAURANT_ID"] = rest.id
        response = create_new_menu(client, form)
        assert response.status_code is not 403

    def test_create_new_reservation_ok(self, client):
        """
        This test case perform the request in order to create
        a new reservation for user john doe
        :param client:
        :return:
        """

        email = "john.doe@email.com"
        pazz = "customer"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        restaurant = (
            db.session.query(Restaurant).filter_by(name="Trial Restaurant").first()
        )
        form = ReservationForm()
        form.restaurant_id = restaurant.id
        form.reservation_date = "23/11/2020 12:00"
        form.people_number = 2

        response = create_new_reservation(client, form)
        assert response.status_code == 200

        # delete data from db
        d1 = datetime.datetime(year=2020, month=11, day=23, hour=12)
        db.session.query(Reservation).filter_by(reservation_date=d1).delete()
        db.session.commit()

    def test_create_new_reservation_ko(self, client):
        """
        This test case perform the request in order to create
        a new reservation for user john doe THAT HAVE TO FAIL
        RESTAURANT IS CLOSED AT 10:00
        :param client:
        :return:
        """

        email = "john.doe@email.com"
        pazz = "customer"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        restaurant = (
            db.session.query(Restaurant).filter_by(name="Trial Restaurant").first()
        )
        form = ReservationForm()
        form.restaurant_id = restaurant.id
        form.reservation_date = "23/11/2020 10:00"
        form.people_number = 2

        response = create_new_reservation(client, form)
        assert response.status_code == 200
        assert "closed" in response.data.decode("utf-8")

    def test_create_new_reservation_unauthorized(self, client):
        """
        not logged client can not book.
        :param client:
        :return:
        """

        restaurant = (
            db.session.query(Restaurant).filter_by(name="Trial Restaurant").first()
        )
        form = ReservationForm()
        form.restaurant_id = restaurant.id
        form.reservation_date = "23/11/2020 12:00"
        form.people_number = 2

        response = create_new_reservation(client, form)
        assert response.status_code == 401

    def test_create_operator(self, client):
        """
        test to create an operator
        """
        # view page
        client.get("/create_operator")

        # POST
        user = UserForm()
        user.firstname = "Steve"
        user.lastname = "Jobs"
        user.email = "steve@apple.com"
        response = create_new_user_with_form(client, user, "operator")

        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

    def test_create_operator_already(self, client):
        """
        test to create an operator with pre-existing email
        """
        user = UserForm()
        user.firstname = "Steve"
        user.lastname = "Jobs"
        user.email = "steve@apple.com"
        response = create_new_user_with_form(client, user, "operator")

        assert response.status_code == 200
        assert "logged_test" not in response.data.decode("utf-8")

    def test_edit_user_data(self, client):
        """
        test edit of user info
        """
        email = "steve@apple.com"
        password = "12345678"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # view page
        client.get("/user/data")

        # POST
        response = client.post(
            "/user/data",
            data=dict(
                email=email,
                firstname="Stefano",
                lastname="Lavori",
                dateofbirth="22/03/1998",
                headers={"Content-type": "application/x-www-form-urlencoded"},
            ),
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "Hi Stefano" in response.data.decode("utf-8")

    def test_delete_user(self, client):
        """
        test delete user url
        """
        email = "steve@apple.com"
        password = "12345678"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = client.get("/user/delete")
        assert response.status_code == 302

    def test_get_user_reservations(self, client):
        """
        test reservation page of customer
        """
        email = "john.doe@email.com"
        password = "customer"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = client.get("/customer/reservations")
        assert response.status_code == 200

    def test_create_restaurant_form(self, client):
        """
        test to create a restaurant
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # view page
        response = client.get("/restaurant/create")
        assert response.status_code == 200

        # POST
        restaurant = RestaurantForm()
        restaurant.name = "Krusty Krab"
        restaurant.phone = "0451245152"
        restaurant.lat = "1"
        restaurant.lon = "1"
        restaurant.n_tables = "1"
        restaurant.cuisine = "Italian food"
        restaurant.open_days = "0"
        restaurant.open_lunch = "11:00"
        restaurant.close_lunch = "12:00"
        restaurant.open_dinner = "20:00"
        restaurant.close_dinner = "21:00"
        restaurant.covid_measures = "masks"
        response = create_new_restaurant_with_form(client, restaurant)
        assert response.status_code == 200
        assert "Register your Restaurant" not in response.data.decode("utf-8")

    def test_create_restaurant_already_form(self, client):
        """
        test to create a restaurant already existent
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # POST
        restaurant = RestaurantForm()
        restaurant.name = "Krusty Krab"
        restaurant.phone = "0451245152"
        restaurant.lat = "1"
        restaurant.lon = "1"
        restaurant.n_tables = "1"
        restaurant.cuisine = "Italian food"
        restaurant.open_days = "0"
        restaurant.open_lunch = "11:00"
        restaurant.close_lunch = "12:00"
        restaurant.open_dinner = "20:00"
        restaurant.close_dinner = "21:00"
        restaurant.covid_measures = "masks"
        response = create_new_restaurant_with_form(client, restaurant)
        assert response.status_code == 200
        assert "Register your Restaurant" in response.data.decode("utf-8")

        db.session.query(Restaurant).filter_by(name=restaurant.name).delete()
        db.session.query(OpeningHours).delete()
        db.session.commit()

    def test_edit_restaurant_data(self, client):
        """
        test edit of restaurant info
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # view page
        response = client.get("/restaurant/data")
        assert response.status_code == 200

        # POST
        # TODO: still miss the logic there

    def test_create_and_delete_table(self, client):
        """
        test to create a table and then destroy it
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        table = RestaurantTable()
        table.restaurant_id = "1"
        table.max_seats = "4"
        table.name = "TestTable123"
        response = create_new_table(client, table)
        assert response.status_code == 200
        assert table.name in response.data.decode("utf-8")

        table = db.session.query(RestaurantTable).filter_by(name="TestTable123").first()
        assert table is not None

        response = client.get("/restaurant/tables?id=" + str(table.id))
        assert response.status_code == 302

    def test_add_photo(self, client):
        """
        test to create a photo
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        photo = PhotoGalleryForm()
        photo.caption = "photo"
        photo.url = "https://www.google.com/pic.jpg"
        response = create_new_photo(client, photo)
        assert response.status_code == 200
        assert photo.caption in response.data.decode("utf-8")

    def test_delete_reservation(self, client):
        """
        check if dish get deletedS
        """
        email = "john.doe@email.com"
        password = "customer"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        reservation = db.session.query(Reservation).first()
        assert reservation is not None
        id = reservation.id

        response = client.get("/customer/deletereservations/" + str(id))

        reservation_not_present = db.session.query(Reservation).filter_by(id=id).first()
        assert reservation_not_present is None
