The Bus Ticket Booking System is a web-based application built using Flask, MySQL, HTML/CSS, and Bootstrap that digitizes a simple bus reservation workflow for students and small operators. 
It provides two clear modules: a customer-facing interface for searching and booking tickets, and an admin panel for managing buses and trips.

From the customer side, users can register, log in, and search for buses by selecting a source city, destination city, and travel date.
Matching trips are fetched from the database and displayed with details such as bus number, operator, departure time, fare, and current seat availability. 
Seat availability is calculated dynamically by subtracting confirmed bookings from the bus’s total seats, which helps avoid overbooking and keeps the system consistent. 
After selecting a trip, the customer can enter the number of seats to book; the application validates the input, checks availability, computes the total fare, and stores the confirmed booking with timestamp and status. 
Customers can later visit the My Bookings section to review their past and upcoming trips in a tabular format.

On the admin side, the project offers a simple dashboard protected by role-based access control using Flask sessions. 
Admin users can add new buses with a bus number, operator name, and total seats, and can create trip entries by choosing a bus and specifying route, date, departure time, and fare. 
All admin operations write directly to the MySQL database, making the data persistent and easy to query. 
Non-admin users are prevented from accessing admin URLs, keeping the management functions separate from normal customers.

This mini project demonstrates key concepts of full‑stack web development: routing and templates in Flask, CRUD operations with MySQL, session management for authentication, form handling, and basic UI design with Bootstrap. 
It can be used as a learning reference for students who want to see how a practical reservation system can be implemented end to end, and it also serves as a base for future enhancements such as online payments, email notifications, ticket PDFs, cancellation, and seat map selection.
