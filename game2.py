class Card:
	def __init__(self, faceValue, suit):
		self.suit = suit
		self.faceValue = faceValue

		if isinstance(faceValue, int) == True:
			self.value = faceValue
		elif faceValue == "A":
			self.value = 11 #remember option to change to 1 if hand is more than 2 cards
		else: #picture card
			self.value = 10

	def define(self): #print details of card
		print str(self.faceValue) + " of " + self.suit

from random import shuffle

class Deck:
	def __init__(self, numberOfDecks = 1):
		self.numberOfDecks = numberOfDecks
		self.allCards = []
		self.discardPile = []
		self.penetrationRate = 0.3

		allSuits = ["Diamonds", "Clubs", "Hearts", "Spades"]
		
		#initializing the full shoe/decks
		for i in range(0, self.numberOfDecks):
			for suit in allSuits:
				for faceValue in range(2,11):
					self.allCards.append(Card(faceValue = faceValue, suit = suit))
				self.allCards.append(Card(faceValue = "A", suit = suit))
				self.allCards.append(Card(faceValue = "J", suit = suit))
				self.allCards.append(Card(faceValue = "Q", suit = suit))
				self.allCards.append(Card(faceValue = "K", suit = suit))

		shuffle(self.allCards)

	def summary(self):
		for card in self.allCards:
			print str(card.faceValue) + " of " + card.suit

	def draw(self):
		if len(self.allCards) > self.penetrationRate * 52 * self.numberOfDecks:
			return self.allCards.pop(0)
		else:
			cardsToRecycle = len(self.discardPile)
			for i in range(0,cardsToRecycle):
				self.allCards.append(self.discardPile.pop(0))
			shuffle(self.allCards)
			return self.allCards.pop(0)

	def reshuffle(self):
		shuffle(self.allCards)

	def numberOfCards(self):
		print str(len(self.allCards))

#load optimal strategies
import csv

fileOpen = open("optimal strategy.csv", "rU")
fileRead = csv.reader(fileOpen)
fileRaw = []
for fileRow in fileRead:
	fileRaw.append(fileRow)

totalDict = {}
ADict = {}
pairDict = {}
for row in fileRaw[1:]:
	if "," not in row[0]:
		totalDict[row[0]] = row[1:]
	elif "A" in row[0] and "A,A" != row[0]:
		if "10" in row[0]:
			ADict[row[0][2:4]] = row[1:]
		else:
			ADict[row[0][2]] = row[1:]
	else:
		if "10" in row[0]:
			pairDict[row[0][0:2]] = row[1:]
		else:
			pairDict[row[0][0]] = row[1:]

fileOpen.close()

#load card counting systems
countingSystemsDict = {}
countingSystemsDict["Hi-Lo"] = [1,1,1,1,1,0,0,0,-1,-1]
countingSystemsDict["Hi-Opt I"] = [0,1,1,1,1,0,0,0,-1,0]
countingSystemsDict["Hi-Opt II"] = [1,1,2,2,1,1,0,0,-2,0]
countingSystemsDict["KO"] = [1,1,1,1,1,1,0,0,-1,-1]
countingSystemsDict["Omega II"] = [1,1,2,2,2,1,0,-1,-2,0]
countingSystemsDict["Red 7"] = [1,1,1,1,1,0.5,0,0,-1,-1]
countingSystemsDict["Zen"] = [1,1,2,2,2,1,0,0,-2,-1]

def countValueOfHand(hand):
	if len(hand) == 2:
		handTotalValue = hand[0].value + hand[1].value
		if handTotalValue == 21:
			handTotalValue = "Blackjack"
	else:
		handTotalValue = 0
		AsCount = 0
		for i in range(0,len(hand)):
			if hand[i].faceValue != "A":
				handTotalValue += hand[i].value
			else:
				AsCount += 1
				handTotalValue += hand[i].value

		if AsCount > 0:
			possibleHandTotalValues = [handTotalValue]
			anotherHandTotalValue = handTotalValue
			while AsCount > 0:
				anotherHandTotalValue -= 10
				possibleHandTotalValues.append(anotherHandTotalValue)
				AsCount -= 1

			chosenValue = 0
			for possibleHandTotalValue in possibleHandTotalValues:
				if possibleHandTotalValue <= 21:
					if possibleHandTotalValue > chosenValue:
						chosenValue = possibleHandTotalValue
					else:
						pass
			if chosenValue == 0: #no values under 21
				chosenValue = 22 #to represent busts

			handTotalValue = chosenValue

		if handTotalValue > 21:
			handTotalValue = 22

	return handTotalValue

def strategy(hand, upcard):
#hand is a list of cards, upcard is dealer's upcard
#returns an action: one of H,S,P
	if len(hand) == 2:
		if hand[0].faceValue == hand[1].faceValue:
			actionOptions = pairDict[str(hand[0].faceValue)]
		else:
			if hand[0].faceValue == "A":
				actionOptions = ADict[str(hand[1].faceValue)]
			elif hand[1].faceValue == "A":
				actionOptions = ADict[str(hand[0].faceValue)]
			else: #no special combinations, just consider total value of hand
				actionOptions = totalDict[str(countValueOfHand(hand))]
	else: #3 or more cards in hand - just consider total value of hand
		handTotalValue = countValueOfHand(hand)
		actionOptions = totalDict[str(handTotalValue)]

	if upcard.faceValue == "A":
		actionOptionsIndex = 8
	elif upcard.faceValue == "J" or upcard.faceValue == "Q" or upcard.faceValue == "K":
		actionOptionsIndex = 7
	else:
		actionOptionsIndex = upcard.faceValue - 2

	action = actionOptions[actionOptionsIndex]
	return action

# hand = [Card("Q", "Clubs"), Card(6, "Diamonds"), Card(6, "Spades")]
# action = strategy(hand, Card(9, "Hearts"))
# print action

winningsList = []
for k in range(0,500): #to get a distribution of the net winnings each simulation
	""" SIMULATION """
	#initialize game
	# bets = range(1,11)
	playingDeck = Deck(numberOfDecks = 6)
	numberOfRounds = 500
	countSystem = "Hi-Lo"
	trueCountsList = []
	trueCount = 0
	profitsList = []
	numberOfPlayers = 6 #exlcuing dealer & player

	for roundNumber in range(0,numberOfRounds):
		if trueCount <= 0 :
			bet = 1 #the minimum bet unit
		else:
			bet = trueCount * 2
		playerHand = []
		dealerHand = []

		#deal cards to dealer
		dealerHand.append(playingDeck.draw())
		dealerHand.append(playingDeck.draw())
		dealerUpcard = dealerHand[0]

		#deal cards to player
		playerHand.append(playingDeck.draw())
		playerHand.append(playingDeck.draw())
		playerHand2 = [] #in case of split

		#player plays
		playerAction = strategy(playerHand, dealerUpcard)
		while playerAction != "S":
			if playerAction == "H":
				playerHand.append(playingDeck.draw())
			elif playerAction == "P":
				playerHand2.append(playerHand.pop(0))
				playerHand.append(playingDeck.draw())
				playerHand2.append(playingDeck.draw())

			playerAction = strategy(playerHand, dealerUpcard)

		playerHandValue = countValueOfHand(playerHand)

		if playerHand2 != []:
			if trueCount <= 0 :
				bet2 = 1 #the minimum bet unit
			else:
				bet2 = trueCount * 2
			playerAction2 = strategy(playerHand2, dealerUpcard)
			while playerAction2 != "S":
				if playerAction2 == "H":
					playerHand2.append(playingDeck.draw())
				elif playerAction2 == "P":
					playerAction2 = "S"
					break

				playerAction2 = strategy(playerHand2, dealerUpcard)

			playerHandValue2 = countValueOfHand(playerHand2)

		#dealer plays
		dealerHandValue = dealerHand[0].value + dealerHand[1].value
		while dealerHandValue < 17:
			dealerCardDrawn = playingDeck.draw()
			dealerHand.append(dealerCardDrawn)
			dealerHandValue = countValueOfHand(dealerHand)
			
		#showdown
		if dealerHandValue == "Blackjack":
			if playerHandValue == "Blackjack":
				winner = "draw"
			else:
				winner = "dealer"
		else:
			if playerHandValue == "Blackjack":
				winner = "player"
			else: #none have blackjack, consider totals
				if dealerHandValue <= 21:
					if playerHandValue <= 21:
						if dealerHandValue > playerHandValue:
							winner = "dealer"
						elif playerHandValue > dealerHandValue:
							winner = "player"
						else: #same value
							winner = "draw"
					else: #player busts
						winner = "dealer"
				else: #dealer busts
					if playerHandValue <= 21:
						winner = "player"
					else: #player also busts
						winner = "draw"

		if winner == "player":
			if playerHandValue == "Blackjack":
				profit = 1.5 * bet
			else:
				profit = bet
		elif winner == "dealer":
			profit = -bet
		else: #push/draw
			profit = 0

		if playerHand2 != []:
			if dealerHandValue == "Blackjack":
				if playerHandValue2 == "Blackjack":
					winner2 = "draw"
				else:
					winner2 = "dealer"
			else:
				if playerHandValue2 == "Blackjack":
					winner2 = "player"
				else: #none have blackjack, consider totals
						if dealerHandValue <= 21:
							if playerHandValue2 <= 21:
								if dealerHandValue > playerHandValue2:
									winner2 = "dealer"
								elif playerHandValue2 > dealerHandValue:
									winner2 = "player"
								else: #same value
									winner2 = "draw"
							else: #player busts
								winner2 = "dealer"
						else: #dealer busts
							if playerHandValue2 <= 21:
								winner2 = "player"
							else: #player also busts
								winner2 = "draw"

			if winner2 == "player":
				if playerHandValue == "Blackjack":
					profit += 1.5 * bet2
				else:
					profit += bet2
			elif winner2 == "dealer":
				profit += -bet2
			else: #push/draw
				profit += 0

		profitsList.append([profit])

		#discard all cards in hand to discard pile
		for j in range(0, numberOfPlayers*3):
			playingDeck.discardPile.append(playingDeck.draw())
		playingDeck.discardPile += dealerHand + playerHand + playerHand2

		#update counts
		runningCount = 0
		for discardCard in playingDeck.discardPile:
			if discardCard.faceValue != "A":
				runningCount += countingSystemsDict[countSystem][discardCard.value - 2]
			else: #the card is an A's
				runningCount += countingSystemsDict[countSystem][9]

		if len(playingDeck.allCards) > playingDeck.penetrationRate * 52 * playingDeck.numberOfDecks:
			trueCount = runningCount/(float(len(playingDeck.allCards))/52)
		else: #the deck will be reshuffled - restart count
			trueCount = 0

		trueCountsList.append([trueCount])

	""" END SIMULATION """
	netProfit = 0
	for profit in profitsList:
		netProfit += profit[0]
	winningsList.append([netProfit])

fileOpen = open("winnings.csv", "w")
fileWrite = csv.writer(fileOpen, delimiter = ',')
fileWrite.writerows(winningsList)























