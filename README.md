# Real Estate Management System (REMS)

A **Flask-based Real Estate Management System** designed to help real estate businesses efficiently manage properties, users, and transactions through a centralized web platform.

---

## Project Overview

The Real Estate Management System (REMS) digitizes and streamlines core real estate operations such as property management, customer handling, and deal tracking. The system reduces manual work, minimizes errors, and improves operational efficiency by providing an intuitive admin dashboard and structured database-driven workflows.

---

## Key Features

* Admin dashboard for managing system data
* Property management (Add / View / Update / Delete)
* User management (Agents & Customers)
* Deal management (Cash, Renting, Installment)
* Transaction and payment tracking
* Property status automation based on deal state
* Reporting-ready database structure

---

## Technologies Used

### Programming Languages

* HTML
* CSS
* JavaScript
* Python
* SQL

### Frameworks & Tools

* Flask
* SQL Server Management Studio (SSMS)
* PYODBC

---

## System Modules & Routes

### Properties

* `/properties` – List properties
* `/properties/add`
* `/properties/update/<property_id>`
* `/properties/delete/<property_id>`

### Agents

* `/agents` – List agents
* `/agents/add`
* `/agents/update/<agent_id>`
* `/agents/delete/<agent_id>`

### Customers

* `/customers`
* `/customers/add`
* `/customers/update/<customer_id>`
* `/customers/delete/<customer_id>`

### Deals

* `/deals`
* `/deals/add`
* `/deals/update/<deal_id>`
* `/deals/delete/<deal_id>`

### Deal Types

* Cash Deals: `/cash_deals`
* Renting Deals: `/renting_deals`
* Installment Deals: `/installment_deals`

### Lookup Tables

* Property Types: `/property_types`
* Features: `/features`

---

## Database Design

The system supports full CRUD operations on the following tables:

* Properties
* Property Types
* Property Features
* Clients
* Agents
* Deals
* Cash Deals
* Renting Deals
* Installment Deals

The database connection is handled using **PYODBC**, with structured error handling and validation for all operations.

---

## Templates Structure

HTML templates are organized by module and rendered using **Jinja2**:

* `properties/` – list, add, update
* `agents/` – list, add, update
* `customers/` – list, add, update
* `deals/` – list, add, update, error, cash/renting/installment views
* `property_types/` – list, add, update
* `features/` – list, add, update
* `index.html` – Main landing page

All templates extend a shared base layout for consistent UI and styling.

---

## Running the Application

1. Ensure SQL Server and ODBC driver are properly configured
2. Update the database connection string if needed
3. Run the application:

```bash
python app.py
```

The Flask development server will start in debug mode.

---

## Future Improvements

* Add role-based authentication and login system
* Introduce agent-specific permissions
* Enhance dashboard analytics and reports
* Improve UI/UX design


---

## Conclusion

REMS provides a practical, scalable solution for real estate businesses seeking to modernize their operations. The project demonstrates effective use of Flask, relational databases, and MVC-style architecture to deliver a reliable management platform.
