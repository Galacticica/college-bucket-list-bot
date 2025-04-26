import discord
from discord.ext import commands
from discord import app_commands
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            # Connect to the database
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            # Check if the user already exists
            cursor.execute('SELECT id FROM "user" WHERE id = %s;', (member.id,))
            user_exists = cursor.fetchone()

            if not user_exists:
                # Insert the new user into the "user" table
                cursor.execute('''
                    INSERT INTO "user" (id, discordid)
                    VALUES (%s, %s);
                ''', (member.id, str(member)))

                # Add all items from the "bucketlist" table to the "user-items" table for the new user
                cursor.execute('''
                    INSERT INTO "user-items" (userid, itemid, status)
                    SELECT %s, id, FALSE FROM "bucketlist";
                ''', (member.id,))

                print(f"User {member.name} added to the database with bucketlist items.")

            # Commit changes and close the connection
            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error: {e}")

    @app_commands.command(name="add_all_members", description="Add all current members to the database")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_all_members(self, interaction: discord.Interaction):
        try:
            # Connect to the database
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            # Iterate through all members in the server
            for member in interaction.guild.members:
                # Skip bots
                if member.bot:
                    continue

                # Check if the user already exists
                cursor.execute('SELECT id FROM "user" WHERE id = %s;', (member.id,))
                user_exists = cursor.fetchone()

                if not user_exists:
                    # Insert the new user into the "user" table
                    cursor.execute('''
                        INSERT INTO "user" (id, discordid)
                        VALUES (%s, %s);
                    ''', (member.id, str(member)))

                    # Add all items from the "bucketlist" table to the "user-items" table for the new user
                    cursor.execute('''
                        INSERT INTO "user-items" (userid, itemid, status)
                        SELECT %s, id, FALSE FROM "bucketlist";
                    ''', (member.id,))

                    print(f"User {member.name} added to the database with bucketlist items.")

            # Commit changes and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            await interaction.response.send_message("All members have been added to the database.", ephemeral=True)
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

    @app_commands.command(name="add_bucketlist_item", description="Add a new item to the bucketlist and update user-items for all users")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_bucketlist_item(self, interaction: discord.Interaction, item_name: str):
        try:
            # Connect to the database
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            # Insert the new item into the bucketlist table
            cursor.execute('''
                INSERT INTO "bucketlist" (item)
                VALUES (%s)
                RETURNING id;
            ''', (item_name,))
            new_item_id = cursor.fetchone()[0]

            # Add the new item to the user-items table for all users
            cursor.execute('''
                INSERT INTO "user-items" (userid, itemid, status)
                SELECT id, %s, FALSE FROM "user";
            ''', (new_item_id,))

            # Commit changes and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            await interaction.response.send_message(f'Bucketlist item "{item_name}" has been added and updated for all users.', ephemeral=True)
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Update(bot))