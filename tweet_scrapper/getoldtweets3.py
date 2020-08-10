import os, sys, re, getopt
import traceback
from tweet_scrapper import GetOldTweets3 as got


def main(username,since,until,maxtweets):
    try:
        opts= [('--username',username),('--since',since),('--until',until),('--maxtweets',maxtweets),('--output','data.csv')]
        tweetCriteria = got.manager.TweetCriteria()
        outputFileName = "output_got.csv"

        debug = False
        usernames = set()
        username_files = set()
        for opt, arg in opts:
            if opt == '--querysearch':
                tweetCriteria.querySearch = arg

            elif opt == '--username':
                usernames_ = [u.lstrip('@') for u in re.split(r'[\s,]+', arg) if u]
                usernames_ = [u.lower() for u in usernames_ if u]
                usernames |= set(usernames_)

            elif opt == '--usernames-from-file':
                username_files.add(arg)

            elif opt == '--since':
                tweetCriteria.since = arg

            elif opt == '--until':
                tweetCriteria.until = arg

            elif opt == '--near':
                geocode = arg.split(',')
                try:
                    if len(geocode) != 2:
                        raise
                    lat, lon = geocode[0].strip(), geocode[1].strip()
                    if lat[-1].lower() == 'n':
                        lat = float(lat[:-1])
                    elif lat[-1].lower() == 's':
                        lat = -float(lat[:-1])
                    else:
                        lat = float(lat)

                    if lon[-1].lower() == 'e':
                        lon = float(lon[:-1])
                    elif lon[-1].lower() == 'w':
                        lon = -float(lon[:-1])
                    else:
                        lon = float(lon)
                    if lat < -180 or lat > 180:
                        raise
                    if lon < -90 or lon > 90:
                        raise
                    tweetCriteria.lat = lat
                    tweetCriteria.lon = lon
                except:
                    tweetCriteria.near = arg

            elif opt == '--within':
                tweetCriteria.within = arg

            elif opt == '--toptweets':
                tweetCriteria.topTweets = True

            elif opt == '--maxtweets':
                tweetCriteria.maxTweets = int(arg)

            elif opt == '--lang':
                tweetCriteria.lang = arg

            elif opt == '--output':
                outputFileName = arg

            elif opt == '--debug':
                debug = True

        if debug:
            print(' '.join(sys.argv))
            print("GetOldTweets3", got.__version__)

        if username_files:
            for uf in username_files:
                if not os.path.isfile(uf):
                    raise Exception("File not found: %s"%uf)
                with open(uf) as f:
                    data = f.read()
                    data = re.sub('(?m)#.*?$', '', data)  # remove comments
                    usernames_ = [u.lstrip('@') for u in re.split(r'[\s,]+', data) if u]
                    usernames_ = [u.lower() for u in usernames_ if u]
                    usernames |= set(usernames_)
                    print("Found %i usernames in %s" % (len(usernames_), uf))

        if usernames:
            if len(usernames) > 1:
                tweetCriteria.username = usernames
                if len(usernames)>20 and tweetCriteria.maxTweets > 0:
                    maxtweets_ = (len(usernames) // 20 + (len(usernames)%20>0)) * tweetCriteria.maxTweets
                    print("Warning: due to multiple username batches `maxtweets' set to %i" % maxtweets_)
            else:
                tweetCriteria.username = usernames.pop()
        value = (f"{outputFileName}")
        outputFile = open(outputFileName, "w+", encoding="utf8")
        outputFile.write('date,username,to,replies,retweets,favorites,text,geo,mentions,hashtags,id,permalink\n')

        cnt = 0
        def receiveBuffer(tweets):
            nonlocal cnt

            for t in tweets:
                data = [t.date.strftime("%Y-%m-%d %H:%M:%S"),
                    t.username,
                    t.to or '',
                    t.replies,
                    t.retweets,
                    t.favorites,
                    '"'+t.text.replace('"','""')+'"',
                    t.geo,
                    t.mentions,
                    t.hashtags,
                    t.id,
                    t.permalink]
                data[:] = [i if isinstance(i, str) else str(i) for i in data]
                outputFile.write(','.join(data) + '\n')

            outputFile.flush()
            cnt += len(tweets)

            if sys.stdout.isatty():
                print("\rSaved %i"%cnt, end='', flush=True)
            else:
                print(cnt, end=' ', flush=True)

        print("Downloading tweets...")
        got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer, debug=debug)

    except getopt.GetoptError as err:
        print('Arguments parser error, try -h')
        print('\t' + str(err))

    except KeyboardInterrupt:
        print("\r\nInterrupted.\r\n")

    except Exception as err:
        print(traceback.format_exc())
        print(str(err))

    finally:
        if "outputFile" in locals():
            outputFile.close()
            print()
            print('Done. Output file generated "%s".' % outputFileName)

            print("Cleaning Tweets...")

            #Cleaning the data
            import pandas as pd
            data_1 = pd.read_csv(value) 
            #Check the tweet content
            data_1.fillna("",inplace=True)
            # Data Cleaning
            #Remove hashtags, links etc
            cleaned_tweets = []
            count = 0
            while count <= (data_1.shape[0])-1:
                val = data_1.text[count]
                remove_links = ' '.join(re.sub(r"http(s)?://((\w+).?){1,}", " ",val).split())
                remove_piclink = re.sub('pic.twitter.com/[A-Za-z0-9]+','',remove_links)
                remove_handles = re.sub(r'@[A-Za-z0-9_]+', '', remove_piclink)
                remove_hashtags = ' '.join(re.sub("#[A-Za-z0-9]+"," ",remove_handles).split())
                remove_dots = re.sub(r'…', '', remove_hashtags)
                cleaned_tweets.append(remove_dots)
                count = count + 1

            data = pd.DataFrame(cleaned_tweets,columns=["Cleaned Tweets"])
            data_1.drop(["text"],axis=1,inplace=True)
            result = pd.concat([data_1,data],1,ignore_index=True)
            result.columns = ['date','username','to','replies','retweets','favorites','geo','mentions','hashtags','id','permalink','tweets']
            cleaned_name = "Cleaned_" + value
            result.to_csv(cleaned_name,index=False)
            print('Done. Cleaned file generated as "%s".' % cleaned_name)


if __name__ == '__main__':
    main()
    
