from telethon.sync import TelegramClient
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil import parser
import json
import string
import re
import os


def saveData():
    names = []
    counts = []
    messageTimes = []
    wordCounts = []
    with open('key') as f:
        key = json.load(f)
    with TelegramClient(key['name'], key['api_id'], key['api_hash']) as client:
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            cnt = 0
            times = []
            wordDict = {}
            if not dialog.is_user:
                continue
            for message in client.iter_messages(dialog, limit=None):
                cnt += 1
                times.append(message.date.isoformat())
                if not isinstance(message.text, str):
                    continue
                stringWithoutPunctuation = message.text.translate(str.maketrans('', '', '!\"#$%&\'()*+,./:;<=>?@[\]^_`{|}~'))#re.sub("[^\w\s]", "", message.text)
                wordList = stringWithoutPunctuation.split()
                for word in wordList:
                    if len(word) <= 2:
                        continue
                    if word.lower() in wordDict:
                        wordDict[word.lower()] += 1
                    else:
                        wordDict[word.lower()] = 1
            print(dialog.name, cnt)
            names.append(dialog.name)
            counts.append(cnt)
            messageTimes.append(times)
            wordCounts.append(wordDict)
    aux = sorted(zip(counts, names, messageTimes, wordCounts), reverse=True)
    _counts = [x for x, y, z, w in aux]
    _names = [y for x, y, z, w in aux]
    _messageTimes = [z for x, y, z, w in aux]
    _wordCounts = [w for x, y, z, w in aux]
    with open('data', 'w') as f:
        json.dump({'names': _names, 'counts': _counts, 'messageTimes': _messageTimes, 'wordCounts': _wordCounts}, f)


def readData():
    with open('data') as f:
        data = json.load(f)
    _messageTimes = data['messageTimes']
    messageTimes = []
    for l in _messageTimes:
        tmpList = []
        for d in l:
            tmpList.append(parser.isoparse(d))
        messageTimes.append(tmpList)
    return data['names'], data['counts'], messageTimes


def plotActivity(names, messageTimes, startDate, n_bins, threshold, filename):
    fig, ax = plt.subplots()
    plt.xlim(startDate, datetime.now())
    myBins = [startDate]
    while myBins[-1] < datetime.now():
        myBins.append(myBins[-1] + (datetime.now() - startDate) / n_bins)
    for i in range(len(names)):
        if len(messageTimes[i]) >= threshold:
            ax.hist(messageTimes[i], histtype='step', fill=False, label=names[i], bins=myBins)
    plt.legend()
    fig.autofmt_xdate()
    plt.savefig(filename, dpi=200)
    plt.yscale('log')
    plt.savefig(filename + 'Log', dpi=200)


def plotOnePersonActivity(names, messageTimes, nbins=50, threshold=1000):
    for i in range(len(names)):
        if len(messageTimes[i]) < threshold:
            continue
        fig, ax = plt.subplots()
        ax.hist(messageTimes[i], histtype='step', fill=False, bins=nbins)
        fig.autofmt_xdate()
        plt.savefig(names[i] + str(nbins), dpi=200)
        plt.close()


def plotCounts(names, counts, filename):
    fig, ax = plt.subplots()
    rng = range(1, len(names) + 1)
    ax.scatter(rng, counts)
    plt.savefig(filename, dpi=200)
    plt.yscale('log')
    plt.savefig(filename + 'Log', dpi=200)
    plt.xscale('log')
    plt.savefig(filename + 'LogLog', dpi=200)


if __name__ == '__main__':
    #if 'data' not in os.listdir('./'):  # checks if there is a file with the data already
    #saveData()

    names, counts, messageTimes = readData()

    plotOnePersonActivity(names, messageTimes, nbins=50)
    plotActivity(names, messageTimes, datetime(2018, 1, 1, 0, 0, 0), 50, 5000, 'activity2018_50_5000')
    plotCounts(names, counts, 'msgCounts')
