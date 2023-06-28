'''
This script checks the console log of Left 4 Dead 2 for players that are possible cheaters
and prints the results to the user.

-condebug must be enabled in the launch options (click properties on the Left 4 Dead 2 file on steam)

Using the console type 'status', this will send all player IDs into the log for the script to parse.

If any suspected cheaters are found the result will be printed in the command line.
'''
if __name__ == '__main__':
    # Imports
    import requests
    import bs4
    from steamid_converter import Converter
    import pyperclip
    import time

    while True:
        non_cheaters = [] 
        # Check for status command input into L4D2 console
        file = open("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Left 4 Dead 2\\left4dead2\\console.log",'r',encoding='utf-8')
        logfile = [i for i in file.readlines()]
        for log in logfile:
            if 'hostname:' in log:
                index = logfile.index(log)
                logfile = logfile[index:]
                with open("C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\console.log",'w') as file:
                    file.write('')

                # Parse the log to find SteamIDs and convert them into useable profile URLs.
                playerURLs = []
                no_dupes = []
                for log in logfile:
                    split_list = log.split(' ')
                    for i in split_list:
                        if 'STEAM_' in i:
                            if i not in no_dupes:
                                no_dupes.append(i)
                                playerURLs.append('https://steamcommunity.com/profiles/' + str(Converter.to_steamID64(i)))

                # Enter the URL of the player's profile page.
                for url in playerURLs:
                    if url[-1] !='/':
                        url = str(url) + '/'

                    try:
                        # Making the request and creating the soup.
                        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"} 
                        request = requests.get(str(url) + 'allcomments',headers=headers)
                        soup = bs4.BeautifulSoup(request.content,'lxml')

                        # Parsing for the name of the player.
                        name = [i.text.strip() for i in soup.find_all('a',class_='whiteLink persona_name_text_content')][0]

                        # Parsing the soup for authors and their comments.
                        authors = [''.join(''.join(''.join(i.text.strip().split('\t')).split('\n')).split('\r')) for i in soup.find_all('div',class_='commentthread_comment_author')]
                        text = [''.join(''.join(''.join(i.text.strip().split('\t')).split('\n')).split('\r')) for i in soup.find_all('div',class_='commentthread_comment_text')]
                        comments = list(zip(authors,text))

                        # Suspicious keywords list.
                        keywords = ['cheat','cheating','cheats','cheatz','cheater',
                                   'hack','hacking','hacks','hackz','hax','hacker',
                                   'script','scripting','scripts','scriptz','scripter',
                                   'aimbot','wallhacks','wallhackz',
                                   'Cheat','Cheating','Cheats','Cheatz','Cheater',
                                   'Hack','Hacking','Hacks','Hackz','Hax','Hacker',
                                   'Script','Scripting','Scripts','Scriptz','Scripter',
                                   'Aimbot','Wallhacks','Wallhackz']

                        # Looking for keywords in all the comments and appending to the list of callouts.
                        callouts = []
                        for comment in comments:
                            for keyword in keywords:
                                if keyword in comment[1]:
                                    if comment not in callouts:
                                        callouts.append(comment)

                        # VAC ban check.
                        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"} 
                        request = requests.get(url,headers=headers)
                        soup = bs4.BeautifulSoup(request.content,'lxml')
                        VAC_ban = [''.join(''.join(i.text.strip().split('\t')).split('\n\r\n')) for i in soup.find_all('div',class_='profile_ban_status')]

                        # Private check.
                        private_check = [i.text.strip() for i in soup.find_all('div', class_='profile_private_info')]

                        # Print any players with VAC bans or suspicious comments. 
                        if len(VAC_ban) > 0 or len(callouts) > 0:

                            string = ''

                            # Begin joining the results starting with the player's name.
                            string = string + 'Player name: ' + name + ', '

                            # Concat private check.
                            if len(private_check) > 0:
                                string = string + str(private_check[0])
                                # Concat any VAC ban on record or print that none were found.
                                if len(VAC_ban) > 0:
                                    string = string + str(VAC_ban[0])
                                else:
                                    string = string + 'No VAC ban on record.'

                            else:
                                # Concat the number of suspicious comments.
                                string = string + 'Comments on profile page that mention cheats, hacks or scripts: ' + str(len(callouts)) + ', '

                                # Concat any VAC ban on record or print that none were found.
                                if len(VAC_ban) > 0:
                                    string = string + str(VAC_ban[0])
                                else:
                                    string = string + 'No VAC ban on record.'

                            print(string)

                            # Print space between results.
                            print('')

                            for callout in callouts:
                                print(' Comment on profile:','"' + str(callout[1]) + '", ')

                            print(' ')
                            print('--------------------------------------------------------------------------------------------')
                        else:
                            non_cheaters.append(url)

                    except:
                        print('No user found with that URL.')


                if len(playerURLs) == len(non_cheaters):
                    print('No evidence of cheating found.')
                pyperclip.copy('status')
                print('The word "status" has been copied to your clipboard.')

        # Wait 10 seconds before checking for new status command entry.
        print('Awaiting status command...')
        time.sleep(30)