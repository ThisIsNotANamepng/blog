tags:Boilerplate
date:2024-08-19
# Boilerplates

Whenever I start a project I often realize I don't remember all of the fundamental syntax to setting up some code or library, so I keep some snippets to get me started here

## Flask

    from flask import Flask, request, jsonify
    import sqlite3

    app = Flask(__name__)

    # Function to access SQLite database
    def access_database():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table_name')
        data = cursor.fetchall()
        conn.close()
        return data

    @app.route('/get_data', methods=['GET'])
    def get_data():
        # Accessing query parameters from URL
        param_value = request.args.get('param_name')
        # Accessing data from database
        db_data = access_database()
        return jsonify({'param_value': param_value, 'database_data': db_data})

    @app.route('/process_data', methods=['GET', 'POST'])
    def process_data():
        if request.method == 'GET':
            param_value = request.args.get('param_name')
            db_data = access_database()
            return jsonify({'param_value': param_value, 'database_data': db_data})
        elif request.method == 'POST':
            data = request.json
            return jsonify({'message': 'Data submitted successfully'})
        else:
            return "Invalid mode"

    if __name__ == '__main__':
        app.run(debug=True)


## Tensorflow

    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.losses import SparseCategoricalCrossentropy
    from tensorflow.keras.metrics import SparseCategoricalAccuracy

    # Example data loading (replace with your own data loading code)
    # X_train, y_train = load_data()

    # Define the model
    model = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(10, activation='softmax')
    ])

    # Compile the model
    model.compile(optimizer=Adam(learning_rate=0.001),
                loss=SparseCategoricalCrossentropy(),
                metrics=[SparseCategoricalAccuracy()])

    # Print model summary
    model.summary()

    # Example training (replace with your own training code)
    # history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

    # Example inference (replace with your own inference code)
    # y_pred = model.predict(X_test)

    # Evaluate the model
    # loss, accuracy = model.evaluate(X_test, y_test)
    # print(f'Test loss: {loss:.4f}')
    # print(f'Test accuracy: {accuracy:.4f}')

## Pandas CSV

    import pandas as pd

    # Load CSV file into a DataFrame
    file_path = 'your_file_path.csv'  # Replace with your CSV file path
    df = pd.read_csv(file_path)

    # Display basic information about the DataFrame
    print("Shape of the DataFrame:")
    print(df.shape)  # Display number of rows and columns
    print("\nColumn names:")
    print(df.columns)  # Display column names
    print("\nData types:")
    print(df.dtypes)  # Display data types of each column

    # Display first few rows of the DataFrame
    print("\nFirst 5 rows:")
    print(df.head())

    # Basic manipulations
    # Example: Selecting specific columns
    selected_columns = ['column_name1', 'column_name2']
    subset_df = df[selected_columns]

    # Example: Filtering rows based on a condition
    filtered_df = df[df['column_name'] > 100]

    # Example: Adding a new column
    df['new_column'] = df['existing_column1'] + df['existing_column2']

    # Example: Grouping and aggregating data
    grouped_df = df.groupby('grouping_column').agg({'aggregated_column': 'mean'})

    # Example: Sorting DataFrame by column
    sorted_df = df.sort_values(by='sorting_column', ascending=False)

    # Display modified DataFrame or results of manipulations
    print("\nSubset DataFrame:")
    print(subset_df.head())

    print("\nFiltered DataFrame:")
    print(filtered_df.head())

    print("\nDataFrame with new column:")
    print(df.head())

    print("\nGrouped and Aggregated DataFrame:")
    print(grouped_df.head())

    print("\nSorted DataFrame:")
    print(sorted_df.head())

## HTML

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>I hate frontend</title>
        <style>
            /* Add your CSS styles here */
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
                padding: 0;
            }
            /* Example of CSS styles */
            .container {
                max-width: 800px;
                margin: auto;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            p {
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>HTML Sucks</h1>
            </header>
            <main>
                <section id="section1">
                    <h2>Section 1</h2>
                    <p>This is some content for section 1.</p>
                </section>
                <section id="section2">
                    <h2>Section 2</h2>
                    <p>This is some content for section 2.</p>
                </section>
            </main>
            <footer>
                <p>&copy; 2024 My Company. All rights reserved.</p>
            </footer>
        </div>
    </body>
    </html>

## CSS (File)

    /* This is a comment */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        background-color: #f0f0f0;
        color: #333;
    }

    .container {
        max-width: 1200px;
        margin: auto;
        padding: 20px;
    }

    header {
        text-align: center;
        margin-bottom: 20px;
    }

    header h1 {
        font-size: 2.5em;
        color: #333;
    }

    main {
        padding: 20px;
    }

    section {
        margin-bottom: 40px;
    }

    h2 {
        font-size: 1.8em;
        color: #555;
        margin-bottom: 10px;
    }

    p {
        font-size: 1.1em;
        line-height: 1.8;
        color: #666;
    }

    footer {
        text-align: center;
        padding: 10px 0;
        background-color: #333;
        color: #fff;
        position: fixed;
        bottom: 0;
        width: 100%;
    }
