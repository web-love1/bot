import discord
from discord.ext import commands
import aiohttp

# 1. ตั้งค่าพื้นฐานของบอท
intents = discord.Intents.default()
intents.message_content = True  # เปิดใช้งานการอ่านข้อความ
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ LOGIN : {bot.user}')

# 2. คำสั่ง !i สำหรับเรียกข้อมูล
@bot.command(name='i')
async def get_election_info(ctx, cid: str = None):
    # ตรวจสอบเบื้องต้นว่าใส่เลขมาหรือไม่
    if cid is None or len(cid) != 13 or not cid.isdigit():
        await ctx.send("❌ กรุณาระบุเลข 13 หลักให้ถูกต้อง เช่น `!i 11020000xxxxx`")
        return

    # URL ของ API กรมการปกครอง
    url = f"https://boraservices.bora.dopa.go.th/api/election/v1/nenuit/{cid}"

    # แจ้งเตือนว่ากำลังค้นหา (เผื่อ API ตอบสนองช้า)
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        raw_data = await response.json()
                        
                        # ตรวจสอบโครงสร้างข้อมูล (List -> dict -> nvpop)
                        if isinstance(raw_data, list) and len(raw_data) > 0:
                            data = raw_data[0].get('nvpop', {})
                            
                            # ดึงค่าตัวแปรต่างๆ
                            name = data.get('tfname', 'ไม่พบชื่อ')
                            seq = data.get('seq', '-')
                            area = data.get('earea', '-')
                            unit = data.get('eunit', '-')
                            # ลบเครื่องหมาย # ออกจากที่อยู่เพื่อให้ดูสวยงาม
                            location = data.get('desp', 'ไม่ระบุ').replace('#', ' ')
                            
                            # สร้าง Embed แสดงผล
                            embed = discord.Embed(
                                title="🗳️ ผลการค้นหา DOPA 🗳️",
                                color=discord.Color.gold()
                            )
                            embed.add_field(name="", value=f"**@{ctx.author} - ข้อมูลเลือกตั้ง**", inline=False)
                            embed.add_field(name="📋 ข้อมูลการค้นหา", value="", inline=False)
                            embed.add_field(name="ประเภท", value="🆔 บัตรประชาชน", inline=True)
                            embed.add_field(name="ค้นหา", value=cid, inline=True)
                            embed.add_field(name="แหล่งข้อมูล", value="กรมการปกครอง", inline=False)
                            embed.add_field(name="🗳️ ข้อมูลการเลือกตั้ง", value="", inline=False)
                            embed.add_field(name="หน่วยเลือกตั้ง", value=location, inline=False)
                            embed.add_field(name="วันที่เลือกตั้ง", value="2569-02-08", inline=True)
                            embed.add_field(name="ลำดับที่", value=seq, inline=True)
                            embed.set_footer(text=f"ค้นหาโดย: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                            
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send(f"⚠️ ไม่พบข้อมูลสำหรับเลข `{cid}`")
                    
                    elif response.status == 404:
                        await ctx.send("❌ ไม่พบข้อมูล (404 Not Found)")
                    else:
                        await ctx.send(f"🔴 API ขัดข้อง (Status: {response.status})")
            
            except Exception as e:
                await ctx.send(f"❗ เกิดข้อผิดพลาดในการเชื่อมต่อ: `{str(e)}`")

# 3. รันบอท
bot.run('')
