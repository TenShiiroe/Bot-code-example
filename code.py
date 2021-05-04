import discord
import asyncio
import random
import os
from github import Github
import ast #cause why not 
client = discord.Client()
TOKEN = os.environ['TOKEN']
g = Github(os.environ['GG'])

#too lazy to bother with actually usable code(@bot.event / @bot.command)
@client.event         
async def on_message(message):
    #so he won't react to own messages
    if message.author == client.user:
        return
    
    #inv function to get the inv content
    if message.content.startswith("//inv"):
        
        repo = g.get_user().get_repo('Txt-')   #get repo with inventories
        all_files = []
        contents = repo.get_contents("")
        while contents:                 #loop through every file  
            cco = contents.pop(0)
            all_files.append(str(cco).replace('ContentFile(path="','').replace('.txt")',''))   #get every file name  
        #set if the author for either mentioned user or message author     
        if len(message.mentions) == 1: 
            autohr = message.mentions[0]
        elif len(message.mentions) == 0:  
            autohr = message.author
        else:
            await message.channel.send("`Please only mention 1 user`")
            return    
        #look if the user has inv created, if yes, desc = 1, otherwise 0   
        if str(autohr.id) in all_files:
            contents = repo.get_contents(f"{autohr.id}.txt")
            if len(contents.decoded_content.decode()) < 3:
                desc = 0
            else:       
                desc = 1
        else:
            desc = 0
        #if the inv is existing and isn't empty:  (sorry, was lazy renaming the labels so that they're undersandable)
        if desc == 1:
            t = contents.decoded_content.decode()
            tt =[x+1 for x in [len(y) for y in t.splitlines()]]   #split by new lines cause 1 item = 1 line
            final = [sum(tt[:x+1])-1 for x in range(len(tt))]     #get new line "\n" positions
            isa = 0
            newl = []
            for x in final:       #if the text is longer than 1900 char(cause message cap is ~2000), add "split point"
                if x >= 1900+isa:
                    newl.append(x)
                    isa = x
            newl.append(final[-1])
            start = 0
            #if inv exists, split into ~1900char long blocks, wanted to make a def() function inside this one for embeds but it kept failing(even with async - idk why) 
            for x in newl:  
                embed = discord.Embed(title = autohr.name, description = t[start:x], colour = 0xFF0000)
                embed.set_thumbnail(url = autohr.avatar_url)
                embed.set_author(name = "Inventory of")      
                await message.channel.send(embed = embed)
                start = x+1
        #if inv is empty or diesn't exist, cannot be bothered by solving problems so I just copypasted it from above        
        else:
            embed = discord.Embed(title = autohr.name, description = "Your inventory is empty.", colour = 0xFF0000)
            embed.set_thumbnail(url = autohr.avatar_url)
            embed.set_author(name = "Inventory of")      
            await message.channel.send(embed = embed)
        return
        
    #function for adding items to inv
    if message.content.startswith("//iadd"):
        repo = g.get_user().get_repo('Txt-')  #get repo with inventories
        all_files = []
        contents = repo.get_contents("")
        while contents:                          #loop through every file  
            cco = contents.pop(0)
            all_files.append(str(cco).replace('ContentFile(path="','').replace('.txt")',''))     #get every file name  
            
        if len(message.mentions) == 1:
            autohr = message.mentions[0]
        elif len(message.mentions) == 0:
            autohr = message.author
        else:
            await message.channel.send("`Please only mention 1 user`")   
            return
        
        if str(autohr.id) in all_files:
            contents = repo.get_contents(f"{autohr.id}.txt")   
            #load inv items
            try:    
                all_items = contents.decoded_content.decode().strip().split("\n")
                inv_content = {} #name:[quantity, unit]    
            except Exception:
                #pass 
                await message.channel.send("`*wtf??*`")     #shouldn't be a way to get this exception so           
                return
            for item in all_items:   #loop through ivnentory and make a dict of items
                try:
                    if len(contents.decoded_content.decode()) < 3:
                        break
                    name = item.split("-")[0].strip()
                    quantity = item.split("-")[1].strip()
                    quan = int(quantity.split("[")[0].strip())
                    inv_content[name] = [quan,quantity.split("[")[1].replace("]","").strip()]
                except Exception:
                    await message.channel.send("`removing inventory errors`")  #if there is error in formating
            try:    #load message
                if len(message.content[6:].split(",")) > 3: #cause ppl 
                    await message.channel.send("```Please input //iadd [item name], [no of items to add], [unit(no need if the item already exists)]```")
                    return
                if autohr == message.author:
                    mess = message.content[6:].split(",")
                else:
                    mess = message.content[6:].replace(f"<@!{message.mentions[0].id}>","").split(",")
                add_item = mess[0].strip()  #set item to add
                quan_add = int(mess[1].strip())  #set value to add
                if quan_add < 1: #so they cannot add 0 or negative
                    await message.channel.send("`Quantitiy cannot be below 1 for adding items`") 
                    return
                if add_item in inv_content.keys(): #if item is in inv
                    inv_content[add_item][0] = inv_content[add_item][0] + quan_add
                else:  #if it isn't in the inv, add it
                    unit = mess[2].strip()
                    inv_content[add_item] = [quan_add, str(unit)]
                #upload new inv
                final_string = ""
                for item_name in inv_content: 
                    if inv_content[item_name][0] == 0:  #delete items with value 0(cause that's nothing)
                        pass
                    else:
                        final_string = final_string + item_name + " - " + str(inv_content[item_name][0]) + f"[{inv_content[item_name][1]}]\n"
                repo.update_file(contents.path,"Bruh inv add-update", final_string, contents.sha, branch="master") #upload repo
                await message.channel.send("Item added.")             
            except Exception:
                await message.channel.send("```Please input //iadd [item name], [no of items to add], [unit(no need if the item already exists)]```") #for some ppl
        else:  #if inventory isn't existing
            if len(message.content[6:].split(",")) > 3: 
                await message.channel.send("```Please input //iadd [item name], [no of items to add], [unit(no need if the item already exists)]```")
                return
            try:                                                  #Literally the same thing as above cause why not(def functions aren't working - sad)
                if autohr == message.author:
                    mess = message.content[6:].split(",")
                else:
                    mess = message.content[6:].replace(f"<@!{message.mentions[0].id}>","").split(",")
                add_item = mess[0].strip()
                quan_add = int(mess[1].strip())
                unit = mess[2].strip()
                final = add_item + " - " + str(quan_add) + f"[{unit}]\n"
                repo.create_file(f"{message.mentions[0].id}.txt", "creatin repoo", final, branch="master") #create file insted of updating
                await message.channel.send("Item added.")     
            except Exception:
                await message.channel.send("```Please input //iadd [item name], [no of items to add], [unit(no need if the item already exists)]```")
        return
                    
         #delete item from inv literally copypaste of //iadd with one change (cause it'll be easier to find(added and deleted items) in discord history and again def functions aren't working so 
    if message.content.startswith("//idel"):       #same as above but the plottwist is that //idel was created first
        repo = g.get_user().get_repo('Txt-')  #get repo with inventories
        all_files = []
        contents = repo.get_contents("")
        while contents:                          #loop through every file  
            cco = contents.pop(0)
            all_files.append(str(cco).replace('ContentFile(path="','').replace('.txt")',''))     #get every file name  
            
        if len(message.mentions) == 1:
            autohr = message.mentions[0]
        elif len(message.mentions) == 0:
            autohr = message.author
        else:
            await message.channel.send("`Please only mention 1 user`")   
            return
        
        if str(autohr.id) in all_files:
            contents = repo.get_contents(f"{autohr.id}.txt")   
            #load inv items
            try:    
                all_items = contents.decoded_content.decode().strip().split("\n")
                inv_content = {} #name:[quantity, unit]    
            except Exception:
                #pass 
                await message.channel.send("`*wtf??*`")     #shouldn't be a way to get this exception so           
                return
            for item in all_items:   #loop through ivnentory and make a dict of items
                try:
                    if len(contents.decoded_content.decode()) < 3:
                        break
                    name = item.split("-")[0].strip()
                    quantity = item.split("-")[1].strip()
                    quan = int(quantity.split("[")[0].strip())
                    inv_content[name] = [quan,quantity.split("[")[1].replace("]","").strip()]
                except Exception:
                    await message.channel.send("`removing inventory errors`")  #if there is error in formating
            try:    #load message
                if len(message.content[6:].split(",")) > 2: #cause ppl 
                    await message.channel.send("```Please input //idel [item name], [no of items to delete]```")
                    return
                if autohr == message.author:
                    mess = message.content[6:].split(",")
                else:
                    mess = message.content[6:].replace(f"<@!{message.mentions[0].id}>","").split(",")
                del_item = mess[0].strip()  #set item to delete
                quan_del = int(mess[1].strip())  #set value to delete
                if del_item in inv_content.keys(): #if item is in inv
                    if quan_del > inv_content[del_item][0]: #and value isn't more than the one in inv
                        await message.channel.send("`Cannot delete more, than is in the inventory`")
                        return
                    else:
                        inv_content[del_item][0] = inv_content[del_item][0] - quan_del      
                else:
                    await message.channel.send("`Item could not be found in the inventory`")
                    return
                #upload new inv
                final_string = ""
                for item_name in inv_content: 
                    if inv_content[item_name][0] == 0:  #delete items with value 0(cause that's nothing)
                        pass
                    else:
                        final_string = final_string + item_name + " - " + str(inv_content[item_name][0]) + f"[{inv_content[item_name][1]}]\n"
                repo.update_file(contents.path,"Bruh inv del-update", final_string, contents.sha, branch="master") #upload repo
                await message.channel.send("Item deleted.")             
            except Exception:
                await message.channel.send("```Please input //idel [item name], [no of items to delete]```") #for some ppl
        else:  #if inventory isn't existing
            await message.channel.send("`Create your inventory first.`")
        return
    
        #yes/no function to help with decisions
    if message.content.startswith("//yn"):
        decider = random.randint(1, 2)
        if decider == 1:
            #random yes answer
            await message.channel.send(random.choice(["go for it", "you can do it", "I believe in you"]))
            return
        else:
            #random no answer
            await message.channel.send(random.choice(["seems like a bad idea", "you probably shouldn't", "this is too hard for you"]))
            return
        #say sth as a bot
    if message.content.startswith("//a"):
        say_text = message.content[3:]
        await message.delete()
        await message.channel.send(say_text)
        return
    #return mesage content backwards
    if message.content.startswith("//bw"):
                                       #make a list of letters backwards
        letters_list = [message.content[4:].strip()[-(letter+1)] for letter in range(len(message.content[4:].strip()))]
        await message.channel.send("".join(letters_list))
        return
    #actual function, why the bot was created, even thou I could remake it like code above, to make it look "better", it'd lost it's memorable value
    if message.content.startswith("//rpg"):
        user_input = message.content[5:]
        try:      
            split_message = user_input.split(",")  #splits the message 
            ok = len(split_message)
            diff = int(split_message[0].strip())
            stat = int(split_message[1].strip())
            if ok == 2:                              #ah yes, the old way of chcking for errors
                num = random.randint(1, 20)
                last = num + stat
                if num == 1:
                    ans = "Critical fail +0 EXP"   
                elif num == 20:
                    ans = "Critical success +40 EXP"
                elif diff <= last:
                    num = 2 * num
                    ans = "Task successful +" + str(num) + " EXP"
                elif diff > last:
                    num = 1 * num
                    ans = "Task failed +" + str(num) + " EXP"                 #send nice looking embed
                embed = discord.Embed(title = "Charac Nun", description = ans, colour = 0xbf5600)
                embed.set_thumbnail(url = client.user.avatar_url)
                embed.set_author(name = f"stats:{last} - difficulty:{diff} - exp:{num}")      
                await message.channel.send(embed = embed)
                return
            else:
                await message.channel.send("`Please only input 2 numbers`")
                return
        except Exception:
            await message.channel.send("```//rpg [difficulty of the quest], [stat boost]```") 
client.run(TOKEN)
