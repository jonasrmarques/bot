import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")

# Dicionário global para armazenar o histórico das conversas por usuário
historico_conversas = {}

@bot.command()
async def cassino(ctx, *, pergunta):
    nome = ctx.author.name

    if nome not in historico_conversas:
        historico_conversas[nome] = [
            {"role": "system", "content": f"Você é um assistente divertido e inteligente que conversa com o usuário chamado {nome}."}
        ]
    
    # Adiciona a pergunta do usuário no histórico
    historico_conversas[nome].append({"role": "user", "content": pergunta})

    await ctx.send("🎰 Segura aí que tô pensando...")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "messages": historico_conversas[nome],
        "model": "llama3-8b-8192"
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        resposta = response.json()['choices'][0]['message']['content']

        # Adiciona a resposta da IA no histórico para manter contexto
        historico_conversas[nome].append({"role": "assistant", "content": resposta})

        resposta_descontraida = f"🎲 E aí, {nome}! Olha só o que eu achei pra você:\n\n{resposta}\n\n😎 Se quiser mais, só mandar outra!"

        for i in range(0, len(resposta_descontraida), 2000):
            await ctx.send(resposta_descontraida[i:i+2000])
    else:
        await ctx.send("❌ Puts, deu ruim na consulta da Groq. Tenta de novo aí!")


bot.run(DISCORD_TOKEN)
