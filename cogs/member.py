import discord
from discord.ext import commands
from discord import app_commands
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="complete", description="Complete a bucket list item")
    async def complete(self, interaction: discord.Interaction, item_id: int):
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE "user-items"
                SET status = TRUE
                WHERE userid = %s AND itemid = %s;
            ''', (interaction.user.id, item_id))

            cursor.execute('''
                SELECT item
                FROM "bucketlist"
                WHERE id = %s;
            ''', (item_id,))
            item = cursor.fetchone()
            item_name = item[0]

            conn.commit()
            cursor.close()
            conn.close()

            await interaction.response.send_message(f"{item_name} marked as complete.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

    @app_commands.command(name="incomplete", description="Mark a bucket list item as incomplete")
    async def incomplete(self, interaction: discord.Interaction, item_id: int):
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE "user-items"
                SET status = FALSE
                WHERE userid = %s AND itemid = %s;
            ''', (interaction.user.id, item_id))

            cursor.execute('''
                SELECT item
                FROM "bucketlist"
                WHERE id = %s;
            ''', (item_id,))
            item = cursor.fetchone()
            item_name = item[0]

            conn.commit()
            cursor.close()
            conn.close()

            await interaction.response.send_message(f"{item_name} marked as incomplete.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

    @app_commands.command(name="list", description="List all bucket list items")
    async def list_items(self, interaction: discord.Interaction):
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            cursor.execute('''
                SELECT b.id, b.item, ui.status
                FROM "bucketlist" b
                JOIN "user-items" ui ON b.id = ui.itemid
                WHERE ui.userid = %s
                ORDER BY b.id;
            ''', (interaction.user.id,))
            items = cursor.fetchall()

            embed = discord.Embed(
                title="Your Bucket List",
                description="Here are your bucket list items:",
                color=discord.Color.blue()
            )

            if items:
                for index, item in enumerate(items, start=1):
                    status = "✅ Complete" if item[2] else "❌ Incomplete"
                    embed.add_field(
                        name=f"{index}. {item[1]}",
                        value=f"Status: {status}",
                        inline=False
                    )
            else:
                embed.description = "No items found."

            conn.commit()
            cursor.close()
            conn.close()

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")




async def setup(bot):
    await bot.add_cog(Member(bot))
    