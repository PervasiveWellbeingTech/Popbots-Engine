bot_text = "$img$onboarding$img$Hi! ✋ We're the Pop-Bots!\nWe pop in to have simple and brief conversations and help you with your everyday stress \n Please keep each response in one line so we know that you are done 😊\n Sounds good?"

start = bot_text.find("$img$") + len("$img$")
end = bot_text.find("$img$",start)

substring = bot_text[start:end]

print(f"SUBSTRING IS {substring}")
print(f"Start IS {start}")
print(f"end IS {end}")