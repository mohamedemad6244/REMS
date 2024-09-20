#pip install pyodbc
#pip install flask

from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
import pyodbc



app = Flask(__name__)

# Database Connection Function
def get_db_connection():
    try:
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=DESKTOP-P20U83J\SQLEXPRESS;DATABASE=REMS;UID=mohamed.emad6244;PWD=depi123;Trusted_Connection=yes')
        print("Connected Successfully")
        return conn
    except Exception as e:
        print(f"Connection Error: {e}")

get_db_connection()



# Home
@app.route('/', methods=['GET'])
def index():
    try:
        conn=get_db_connection()
        if conn is None:
            return "Database connection failed.", 500
        
        cursor = conn.cursor()
        cursor.execute('SELECT count(*) FROM Properties WHERE Current_Status = ?', ('For Sale',))
        properties_count= cursor.fetchone()[0]

        cursor2=conn.cursor()
        cursor2.execute('SELECT count(*) FROM Properties WHERE Current_Status = ?', ('For Rent',))
        properties_count2= cursor2.fetchone()[0]
        
        cursor3=conn.cursor()
        cursor3.execute('SELECT count(*) FROM Properties WHERE Current_Status = ?', ('Sold',))
        properties_count3= cursor3.fetchone()[0]
        
        cursor4=conn.cursor()
        cursor4.execute('SELECT count(*) FROM Properties')
        properties_count4=cursor4.fetchone()[0]
        
        cursor5=conn.cursor()
        cursor5.execute('SELECT count(*) FROM Agents')
        agents_count=cursor5.fetchone()[0]
        
        cursor6=conn.cursor()
        cursor6.execute('SELECT count(*) FROM Deals WHERE Deal_Status = ?', ('Pending',))
        deals_count=cursor6.fetchone()[0]
        
        cusror7=conn.cursor()
        cusror7.execute('SELECT count(*) FROM Deals WHERE Deal_Status = ?', ('Completed',))
        deals_count2=cursor6.fetchone()[0]
        
        cursor8=conn.cursor()
        cursor8.execute('SELECT count(*) FROM Deals where Deal_Status = ?', ('Cancelled',))
        deals_count3=cursor8.fetchone()[0]
        
        cursor9=conn.cursor()
        cursor9.execute('SELECT count(*) FROM Customers')
        customers_count=cursor9.fetchone()[0]
        
        conn.close()
        
        return render_template('index.html',
                               properties_count=properties_count,
                               properties_count2=properties_count2
                               ,properties_count3=properties_count3
                               ,properties_count4=properties_count4
                               ,agents_count=agents_count,
                               deals_count=deals_count,
                               deals_count2=deals_count2,
                               deals_count3=deals_count3,
                               customers_count=customers_count)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred. Check the server logs for details.", 500


# Properties

## List Properties

@app.route('/properties')
def list_properties():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Properties')
        properties = cursor.fetchall()

        conn.close()

        return render_template('properties/list.html', properties=properties)
    except Exception as e:
        print(f"An error occurred: {e}")  # Print error details to the console
        return "An error occurred. Check the server logs for details.", 500




# ## Add Property
##updated add property

@app.route('/properties/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        try:
            # Extract and validate form data
            type_id = request.form.get('TypeID', None)
            size = request.form.get('Size', '')
            price = request.form.get('Price', '')
            current_status = request.form.get('Current_Status', '')
            city = request.form.get('City', '')
            address_line1 = request.form.get('Address_Line1', '')
            address_line2 = request.form.get('Address_Line2', None)
            state = request.form.get('State', None)
            bathrooms_no = request.form.get('Bathrooms_No', '')
            bedrooms_no = request.form.get('Bedrooms_No', '')
            feature_id = request.form.get('FeatureID', None)
            furniture = request.form.get('Furniture', '')
            listing_date = request.form.get('Listing_Date', '')
            note = request.form.get('Note', None)
            owner_id = request.form.get('Owner_ID', None)

            # Validate required fields
            if not type_id or not size or not price or not current_status or not city or not address_line1 or not listing_date:
                return "Some required fields are missing.", 400

            # Convert and validate integer fields
            try:
                type_id = int(type_id)
                size = int(size)
                price = int(price)
                bathrooms_no = int(bathrooms_no or 0)
                bedrooms_no = int(bedrooms_no or 0)
                furniture = int(furniture)
                feature_id = int(feature_id) if feature_id else None
                owner_id = int(owner_id) if owner_id else None
            except ValueError as e:
                return f"Invalid data provided: {e}", 400

            # Validate constraints
            if price < 0 or furniture not in [0, 1] or current_status not in ['Sold', 'For Rent', 'For Sale', 'Not Available']:
                return "Invalid data provided.", 400

            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO Properties (TypeID, Size, Price, Current_Status, City, Address_Line1, Address_Line2, State, Bathrooms_No, Bedrooms_No, FeatureID, Furniture, Listing_Date, Note, Owner_ID)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (type_id, size, price, current_status, city, address_line1, address_line2, state, bathrooms_no, bedrooms_no, feature_id, furniture, listing_date, note, owner_id))
                conn.commit()
                return redirect(url_for('list_properties'))
            except Exception as e:
                conn.rollback()  # Rollback transaction on error
                print(f"An error occurred during insertion: {e}")
                return "An error occurred during insertion. Check the server logs for details.", 500
            finally:
                conn.close()
        except Exception as e:
            print(f"An error occurred while processing form data: {e}")
            return "An error occurred while processing form data. Check the server logs for details.", 500

    # Fetch property types and features to populate the dropdowns
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TypeID, TypeName FROM PropertyTypes")
    property_types = cursor.fetchall()
    
    cursor.execute("SELECT FeatureID, FeatureName FROM Features")
    features = cursor.fetchall()
    
    conn.close()
    
    return render_template('properties/add.html', property_types=property_types, features=features)




##updated update property

@app.route('/properties/update/<int:property_id>', methods=['GET', 'POST'])
def update_property(property_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Extract form data
        type_id = request.form['TypeID']
        size = int(request.form['Size'])
        price = int(request.form['Price'])
        current_status = request.form['Current_Status']
        city = request.form['City']
        address_line1 = request.form['Address_Line1']
        address_line2 = request.form['Address_Line2']
        state = request.form['State']
        bathrooms_no = int(request.form['Bathrooms_No'])
        bedrooms_no = int(request.form['Bedrooms_No'])
        feature_id = request.form['FeatureID']
        furniture = int(request.form['Furniture'])
        listing_date = request.form['Listing_Date']
        note = request.form['Note']
        owner_id = request.form['Owner_ID']

        # Update database
        try:
            cursor.execute('''
                UPDATE Properties
                SET TypeID=?, Size=?, Price=?, Current_Status=?, City=?, Address_Line1=?, Address_Line2=?, State=?, Bathrooms_No=?, Bedrooms_No=?, FeatureID=?, Furniture=?, Listing_Date=?, Note=?, Owner_ID=?
                WHERE Property_ID=?
            ''', (type_id, size, price, current_status, city, address_line1, address_line2, state, bathrooms_no, bedrooms_no, feature_id, furniture, listing_date, note, owner_id, property_id))
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

        return redirect(url_for('list_properties'))

    # Fetch property by id
    cursor.execute('SELECT * FROM Properties WHERE Property_ID = ?', (property_id,))
    property = cursor.fetchone()
    conn.close()

    return render_template('properties/update.html', property=property)


##delete property

@app.route('/properties/delete/<int:property_id>', methods=['POST'])
def delete_property(property_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM Properties WHERE Property_ID = ?', (property_id,))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    return redirect(url_for('list_properties'))




# Agents
## List Agents


@app.route('/agents')
def list_agents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Example query to ensure License_Number is fetched
        cursor.execute('SELECT * FROM Agents')
        agents = cursor.fetchall()


        conn.close()

        return render_template('agents/list.html', agents=agents)
    except Exception as e:
        print(f"An error occurred: {e}")  # Print error details to the console
        return "An error occurred. Check the server logs for details.", 500


#add agent
@app.route('/agents/add', methods=['GET', 'POST'])
def add_agent():
    if request.method == 'POST':
        try:
            # Extract and validate form data
            first_name = request.form.get('First_Name', '')
            last_name = request.form.get('Last_Name', '')
            phone = request.form.get('Phone_No', '')
            email = request.form.get('Email_Address', '')
            hire_date = request.form.get('Date_Hired', '')
            license_number = request.form.get('License_Number', '')

            # Validate required fields
            if not first_name or not last_name or not phone or not email or not hire_date or not license_number:
                return "Some required fields are missing.", 400

            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO Agents (F_Name, L_Name, Email_Address, Phone_No, Date_Hired, License_Number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (first_name, last_name, email, phone, hire_date, license_number))
                conn.commit()
                return redirect(url_for('list_agents'))
            except Exception as e:
                conn.rollback()  # Rollback transaction on error
                print(f"An error occurred during insertion: {e}")
                return "An error occurred during insertion. Check the server logs for details.", 500
            finally:
                conn.close()
        except Exception as e:
            print(f"An error occurred while processing form data: {e}")
            return "An error occurred while processing form data. Check the server logs for details.", 500

    return render_template('agents/add.html')


#update agent
@app.route('/agents/update/<int:agent_id>', methods=['GET', 'POST'])
def update_agent(agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            first_name = request.form.get('First_Name', '')
            last_name = request.form.get('Last_Name', '')
            phone = request.form.get('Phone_No', '')
            email = request.form.get('Email_Address', '')
            hire_date = request.form.get('Date_Hired', '')
            license_number = request.form.get('License_Number', '')

            if not first_name or not last_name or not phone or not email or not hire_date or not license_number:
                return "Some required fields are missing.", 400

            cursor.execute('''
                UPDATE Agents
                SET F_Name=?, L_Name=?, Email_Address=?, Phone_No=?, Date_Hired=?, License_Number=?
                WHERE Agent_ID=?
            ''', (first_name, last_name, email, phone, hire_date, license_number, agent_id))
            conn.commit()
            return redirect(url_for('list_agents'))
        except Exception as e:
            conn.rollback()  # Rollback transaction on error
            print(f"An error occurred during update: {e}")
            return "An error occurred during update. Check the server logs for details.", 500
        finally:
            conn.close()

    # Fetch agent by id
    cursor.execute('SELECT * FROM Agents WHERE Agent_ID = ?', (agent_id,))
    agent = cursor.fetchone()
    conn.close()

    return render_template('agents/update.html', agent=agent)


#delete agent
@app.route('/agents/delete/<int:agent_id>', methods=['POST'])
def delete_agent(agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM Agents WHERE Agent_ID = ?', (agent_id,))
        conn.commit()
        return redirect(url_for('list_agents'))
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while deleting the agent. Check the server logs for details.", 500
    finally:
        conn.close()




# Customers

## List Customers
@app.route('/customers')
def list_customers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Customers')
        customers = cursor.fetchall()

        conn.close()

        return render_template('customers/list.html', customers=customers)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred. Check the server logs for details.", 500


## Add Customer
@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        try:
            first_name = request.form.get('F_Name', '')
            last_name = request.form.get('L_Name', '')
            phone = request.form.get('Phone', '')
            email = request.form.get('Email', '')
            city = request.form.get('Customer_City', '')

            if not first_name or not last_name or not phone or not email:
                return "Some required fields are missing.", 400

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO Customers (F_Name, L_Name, Phone, Email, Customer_City)
                    VALUES (?, ?, ?, ?, ?)
                ''', (first_name, last_name, phone, email, city))
                conn.commit()
                return redirect(url_for('list_customers'))
            except Exception as e:
                conn.rollback()
                print(f"An error occurred during insertion: {e}")
                return "An error occurred during insertion. Check the server logs for details.", 500
            finally:
                conn.close()
        except Exception as e:
            print(f"An error occurred while processing form data: {e}")
            return "An error occurred while processing form data. Check the server logs for details.", 500

    return render_template('customers/add.html')


## Update Customer
@app.route('/customers/update/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            first_name = request.form.get('F_Name', '')
            last_name = request.form.get('L_Name', '')
            phone = request.form.get('Phone', '')
            email = request.form.get('Email', '')
            city = request.form.get('Customer_City', '')

            if not first_name or not last_name or not phone or not email:
                return "Some required fields are missing.", 400

            cursor.execute('''
                UPDATE Customers
                SET F_Name=?, L_Name=?, Phone=?, Email=?, Customer_City=?
                WHERE Customer_ID=?
            ''', (first_name, last_name, phone, email, city, customer_id))
            conn.commit()
            return redirect(url_for('list_customers'))
        except Exception as e:
            conn.rollback()
            print(f"An error occurred during update: {e}")
            return "An error occurred during update. Check the server logs for details.", 500
        finally:
            conn.close()

    cursor.execute('SELECT * FROM Customers WHERE Customer_ID = ?', (customer_id,))
    customer = cursor.fetchone()
    conn.close()

    return render_template('customers/update.html', customer=customer)


## Delete Customer
@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM Customers WHERE Customer_ID = ?', (customer_id,))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    return redirect(url_for('list_customers'))



## List Deals
@app.route('/deals')
def list_deals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Deals')
        deals = cursor.fetchall()
        conn.close()
        return render_template('deals/list.html', deals=deals)
    except Exception as e:
        print(f"An error occurred: {e}")  # Print error details to the console
        return "An error occurred. Check the server logs for details.", 500


## Add Deal
@app.route('/deals/add', methods=['GET', 'POST'])
def add_deal():
    if request.method == 'POST':
        try:
            # Retrieve form data
            deal_status = request.form.get('deal_status')
            act_end_date = request.form.get('act_end_date')
            property_id = request.form.get('property_id')
            customer_id = request.form.get('customer_id')
            agent_id = request.form.get('agent_id')
            deal_type = request.form.get('deal_type')
            note = request.form.get('note')

            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert into Deals table
            cursor.execute('''
                INSERT INTO Deals (Deal_Status, Deal_Type, Act_End_Date, Property_ID, Customer_ID, Agent_ID, Note)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (deal_status, deal_type, act_end_date, property_id, customer_id, agent_id, note)
            )
            conn.commit()
            deal_id = cursor.execute('SELECT @@IDENTITY').fetchone()[0]

            # Insert into corresponding situational table
            if deal_type == 'Cash':
                cash_deal_price = request.form.get('deal_price')
                cash_deal_date = request.form.get('deal_date')
                upfront_deposit = request.form.get('upfront_deposit')

                cursor.execute('''
                    INSERT INTO Cash_Deals (Deal_ID, Deal_Price, Deal_Date, Upfront_Deposit, Deal_Status)
                    VALUES (?, ?, ?, ?, ?)''',
                    (deal_id, cash_deal_price, cash_deal_date, upfront_deposit, deal_status)
                )
                conn.commit()

            elif deal_type == 'Renting':
                rent_start_date = request.form.get('rent_start_date')
                rent_end_date = request.form.get('rent_end_date')
                monthly_rent = request.form.get('monthly_rent')
                security_deposit = request.form.get('security_deposit')

                cursor.execute('''
                    INSERT INTO Renting_Deals (Deal_ID, Rent_Start_Date, Rent_End_Date, Monthly_Rent, Security_Deposit, Deal_Status)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (deal_id, rent_start_date, rent_end_date, monthly_rent, security_deposit, deal_status)
                )
                conn.commit()

            elif deal_type == 'Installment':
                inst_start_date = request.form.get('inst_start_date')
                inst_end_date = request.form.get('inst_end_date')
                total_price = request.form.get('total_price')
                down_payment = request.form.get('down_payment')
                frequency = request.form.get('frequency')
                installment_amount = request.form.get('installment_amount')

                cursor.execute('''
                    INSERT INTO Installment_Deals (Deal_ID, Inst_Start_Date, Inst_End_Date, Total_Price, Down_Payment, Frequency, Installment_Amount, Deal_Status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (deal_id, inst_start_date, inst_end_date, total_price, down_payment, frequency, installment_amount, deal_status)
                )
                conn.commit()

            # Update property status if needed
            if deal_status == 'Pending':
                cursor.execute('''
                    UPDATE Properties
                    SET Original_Status = Current_Status
                    WHERE Property_ID = ?''',
                    (property_id,)
                )
                conn.commit()

            elif deal_status == 'Completed':
                cursor.execute('''
                    UPDATE Properties
                    SET Current_Status = CASE
                                            WHEN Deal_Type IN ('Cash', 'Installment') THEN 'Sold'
                                            WHEN Deal_Type = 'Renting' THEN 'Rented'
                                            ELSE Current_Status
                                         END,
                        Owner_ID = CASE
                                    WHEN Deal_Type IN ('Cash', 'Installment') THEN ?
                                    ELSE Owner_ID
                                   END
                    WHERE Property_ID = ?''',
                    (customer_id, property_id)
                )
                conn.commit()

            elif deal_status == 'Cancelled':
                cursor.execute('''
                    UPDATE Properties
                    SET Current_Status = Original_Status
                    WHERE Property_ID = ?''',
                    (property_id,)
                )
                conn.commit()

            return redirect(url_for('list_deals'))

        except Exception as e:
            return render_template('deals/error.html', error_message=str(e))
        
        finally:
            cursor.close()
            conn.close()
            
    elif request.method == 'GET':
        return render_template('deals/add.html')


## Update Deal
@app.route('/deals/update/<int:deal_id>', methods=['GET', 'POST'])
def update_deal(deal_id):
    if request.method == 'POST':
        try:
            # Retrieve form data
            deal_status = request.form.get('deal_status')
            act_end_date = request.form.get('act_end_date')
            property_id = request.form.get('property_id')
            customer_id = request.form.get('customer_id')
            agent_id = request.form.get('agent_id')
            deal_type = request.form.get('deal_type')
            note = request.form.get('note')

            # Validate deal_status
            valid_statuses = ['Pending', 'Completed', 'Cancelled']
            if deal_status not in valid_statuses:
                return render_template('deals/error.html', error_message='Invalid deal status.')

            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Update Deals table
            cursor.execute('''
                UPDATE Deals
                SET Deal_Status = ?, Deal_Type = ?, Act_End_Date = ?, Property_ID = ?, Customer_ID = ?, Agent_ID = ?, Note = ?
                WHERE Deal_ID = ?''',
                (deal_status, deal_type, act_end_date, property_id, customer_id, agent_id, note, deal_id)
            )
            conn.commit()

            # Update corresponding situational table based on deal type
            if deal_type == 'Cash':
                cash_deal_price = request.form.get('deal_price')
                cash_deal_date = request.form.get('deal_date')
                upfront_deposit = request.form.get('upfront_deposit')

                cursor.execute('''
                    UPDATE Cash_Deals
                    SET Deal_Price = ?, Deal_Date = ?, Upfront_Deposit = ?
                    WHERE Deal_ID = ?''',
                    (cash_deal_price, cash_deal_date, upfront_deposit, deal_id)
                )
                conn.commit()

            elif deal_type == 'Renting':
                rent_start_date = request.form.get('rent_start_date')
                rent_end_date = request.form.get('rent_end_date')
                monthly_rent = request.form.get('monthly_rent')
                security_deposit = request.form.get('security_deposit')

                cursor.execute('''
                    UPDATE Renting_Deals
                    SET Rent_Start_Date = ?, Rent_End_Date = ?, Monthly_Rent = ?, Security_Deposit = ?
                    WHERE Deal_ID = ?''',
                    (rent_start_date, rent_end_date, monthly_rent, security_deposit, deal_id)
                )
                conn.commit()

            elif deal_type == 'Installment':
                inst_start_date = request.form.get('inst_start_date')
                inst_end_date = request.form.get('inst_end_date')
                total_price = request.form.get('total_price')
                down_payment = request.form.get('down_payment')
                frequency = request.form.get('frequency')
                installment_amount = request.form.get('installment_amount')

                cursor.execute('''
                    UPDATE Installment_Deals
                    SET Inst_Start_Date = ?, Inst_End_Date = ?, Total_Price = ?, Down_Payment = ?, Frequency = ?, Installment_Amount = ?
                    WHERE Deal_ID = ?''',
                    (inst_start_date, inst_end_date, total_price, down_payment, frequency, installment_amount, deal_id)
                )
                conn.commit()

            # Handle status changes
            if deal_status == 'Pending':
                cursor.execute('''
                    UPDATE Properties
                    SET Original_Status = Current_Status
                    WHERE Property_ID = ?''',
                    (property_id,)
                )
                conn.commit()

            elif deal_status == 'Completed':
                cursor.execute('''
                    UPDATE Properties
                    SET Current_Status = CASE
                                            WHEN Deal_Type IN ('Cash', 'Installment') THEN 'Sold'
                                            WHEN Deal_Type = 'Renting' THEN 'Rented'
                                            ELSE Current_Status
                                         END,
                        Owner_ID = CASE
                                    WHEN Deal_Type IN ('Cash', 'Installment') THEN ?
                                    ELSE Owner_ID
                                   END
                    WHERE Property_ID = ?''',
                    (customer_id, property_id)
                )
                conn.commit()

            elif deal_status == 'Cancelled':
                cursor.execute('''
                    UPDATE Properties
                    SET Current_Status = Original_Status
                    WHERE Property_ID = ?''',
                    (property_id,)
                )
                conn.commit()

            return redirect(url_for('list_deals'))

        except Exception as e:
            return render_template('deals/error.html', error_message=str(e))
        
        finally:
            cursor.close()
            conn.close()
            
    elif request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Deals WHERE Deal_ID = ?', (deal_id,))
            deal = cursor.fetchone()
            conn.close()
            if deal:
                return render_template('deals/update.html', deal=deal)
            else:
                return "Deal not found.", 404
        except Exception as e:
            return render_template('deals/error.html', error_message=str(e))


## Delete Deal
@app.route('/deals/delete/<int:deal_id>', methods=['POST'])
def delete_deal(deal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the deal details
        cursor.execute('SELECT Property_ID, Deal_Status FROM Deals WHERE Deal_ID = ?', (deal_id,))
        deal = cursor.fetchone()

        if not deal:
            return "Deal not found.", 404

        property_id, deal_status = deal

        # Delete from situational tables based on deal type
        cursor.execute('SELECT Deal_Type FROM Deals WHERE Deal_ID = ?', (deal_id,))
        deal_type = cursor.fetchone()[0]

        if deal_type == 'Cash':
            cursor.execute('DELETE FROM Cash_Deals WHERE Deal_ID = ?', (deal_id,))
        elif deal_type == 'Renting':
            cursor.execute('DELETE FROM Renting_Deals WHERE Deal_ID = ?', (deal_id,))
        elif deal_type == 'Installment':
            cursor.execute('DELETE FROM Installment_Deals WHERE Deal_ID = ?', (deal_id,))

        # Delete from Deals table
        cursor.execute('DELETE FROM Deals WHERE Deal_ID = ?', (deal_id,))
        conn.commit()

        # Update property status if needed
        if deal_status == 'Pending':
            cursor.execute('''
                UPDATE Properties
                SET Current_Status = Original_Status
                WHERE Property_ID = ?''',
                (property_id,)
            )
            conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('list_deals'))

    except Exception as e:
        return render_template('deals/error.html', error_message=str(e))



@app.route('/property_types', methods=['GET'])
def list_property_types():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM PropertyTypes')
    property_types = cursor.fetchall()
    conn.close()
    return render_template('property_types/list.html', property_types=property_types)


## Add Property Type
@app.route('/property_types/add', methods=['GET', 'POST'])
def add_property_type():
    if request.method == 'POST':
        type_name = request.form['type_name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO PropertyTypes (TypeName) VALUES (?)', (type_name,))
        conn.commit()
        conn.close()
        return redirect(url_for('list_property_types'))
    return render_template('property_types/add.html')

## Update Property Type
@app.route('/property_types/update/<int:type_id>', methods=['GET', 'POST'])
def update_property_type(type_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        type_name = request.form['type_name']
        cursor.execute('UPDATE PropertyTypes SET TypeName = ? WHERE TypeID = ?', (type_name, type_id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_property_types'))
    cursor.execute('SELECT * FROM PropertyTypes WHERE TypeID = ?', (type_id,))
    property_type = cursor.fetchone()
    conn.close()
    return render_template('property_types/update.html', property_type=property_type)

## Delete Property Type
@app.route('/property_types/delete/<int:type_id>', methods=['POST'])
def delete_property_type(type_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM PropertyTypes WHERE TypeID = ?', (type_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_property_types'))

## List Features
@app.route('/features', methods=['GET'])
def list_features():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Features')
    features = cursor.fetchall()
    conn.close()
    return render_template('features/list.html', features=features)

@app.route('/features/add', methods=['GET', 'POST'])
def add_feature():
    if request.method == 'POST':
        feature_name = request.form['feature_name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Features (FeatureName) VALUES (?)', (feature_name,))
        conn.commit()
        conn.close()
        return redirect(url_for('list_features'))
    return render_template('features/add.html')

@app.route('/features/update/<int:feature_id>', methods=['GET', 'POST'])
def update_feature(feature_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        feature_name = request.form['feature_name']
        cursor.execute('UPDATE Features SET FeatureName = ? WHERE FeatureID = ?', (feature_name, feature_id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_features'))
    cursor.execute('SELECT * FROM Features WHERE FeatureID = ?', (feature_id,))
    feature = cursor.fetchone()
    conn.close()
    return render_template('features/update.html', feature=feature)

@app.route('/features/delete/<int:feature_id>', methods=['POST'])
def delete_feature(feature_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Features WHERE FeatureID = ?', (feature_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_features'))

@app.route('/cash_deals', methods=['GET'])
def list_cash_deals():
    connection = get_db_connection()
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM Cash_Deals")
    cash_deals = cursor.fetchall()
    connection.close()
    return render_template('deals/cash_list.html', cash_deals=cash_deals)

@app.route('/renting_deals', methods=['GET'])
def list_renting_deals():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Renting_Deals")
    renting_deals = cursor.fetchall()
    connection.close()
    return render_template('deals/renting_list.html', renting_deals=renting_deals)

@app.route('/installment_deals', methods=['GET'])
def list_installment_deals():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Installment_Deals")
    installment_deals = cursor.fetchall()
    connection.close()
    return render_template('deals/installment_list.html', installment_deals=installment_deals)

if __name__ == '__main__':
    app.run(debug=True, port=8080)