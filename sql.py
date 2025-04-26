import psycopg2

# Heroku database URL (replace with your actual Heroku DB URL)
DATABASE_URL = "postgres://u9r6qf4ueei9s3:p58db04e8282f8e9b0ca20fb40397695d69801f8932922443d47a185bf1606156@c5flugvup2318r.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d2uvdihm5jj10v"

# Connect to the Heroku Postgres database
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Create a table
cursor.execute('''
CREATE TABLE "user"(
    "id" BIGINT NOT NULL,
    "discordid" CHAR(255) NOT NULL
);
ALTER TABLE
    "user" ADD PRIMARY KEY("id");
CREATE TABLE "bucketlist"(
    "id" BIGINT NOT NULL,
    "item" CHAR(255) NOT NULL
);
ALTER TABLE
    "bucketlist" ADD PRIMARY KEY("id");
CREATE TABLE "user-items"(
    "id" BIGINT NOT NULL,
    "userid" BIGINT NOT NULL,
    "itemid" BIGINT NOT NULL,
    "status" BOOLEAN NOT NULL
);
ALTER TABLE
    "user-items" ADD PRIMARY KEY("id");
ALTER TABLE
    "user-items" ADD CONSTRAINT "user_items_itemid_foreign" FOREIGN KEY("itemid") REFERENCES "bucketlist"("id");
ALTER TABLE
    "user-items" ADD CONSTRAINT "user_items_userid_foreign" FOREIGN KEY("userid") REFERENCES "user"("id");
''')

# Commit changes
conn.commit()

# Close the connection
cursor.close()
conn.close()

print("Table created successfully!")
