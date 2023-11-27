import copy


# winshare teamplate with common fields
winshare_template = {
    "additionalPrizeTier": False,
    "page": 0,
    "pageSize": 100,
    "selections": []
}

# wager teamplate with common fields
wager_template = {
    "listIndex": 0,
    "gameName": "",
    "price": 0,
    "boards": []
}


def create_sport_wager(listIndex, stake, matches, miniVakio):
    if stake > 0:
        req = copy.deepcopy(wager_template)

        req["gameName"] = "SPORT"
        req["listIndex"] = listIndex
        req["price"] = stake

        ## this implementation supports only one row (selection) per wager
        if miniVakio:
            req["additionalPrizeTier"] = True
            req["price"] = 2 * stake

        selection = {
            "stake": stake,
            "selections": []
        }

        sysSize = 1
        for m in matches:
            if len(m) == 1:
                outcome = {"outcomes": [m]}
            else:
                sels = []
                for i in m:
                    if i != "\n":
                        sels.append(i)

                outcome = {"outcomes": sels}
                sysSize *= len(sels)

            ## add outcome to selection
            selection["selections"].append(outcome)

        ## add betType based on size
        if sysSize == 1:
            selection["betType"] = "Regular"
        else:
            selection["betType"] = "FREE " + str(sysSize)

        ## ... and the selection to wager request
        req["boards"].append(selection)

    else:
        req = copy.deepcopy(winshare_template)

        for m in matches:
            if len(m) == 1:
                outcome = {"outcomes": [m]}
            else:
                sels = []
                for i in m:
                    if i != "\n":
                        sels.append(i)

                outcome = {"outcomes": sels}

            ## add outcome to selection
            req["selections"].append(outcome)

    return req
