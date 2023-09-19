//
//  blackjack.cpp
//  blackjack
//
//  Created by Leander Lu on 2/15/22.
//

/*Leander Lu
  lxlu@usc.edu */
/* This code is programmed to play blackjack. The shuffle function was written
following the Fisher-Yates shuffle algorithm, as well as initializing the
"cards" array. Printcard uses if-else statements to print out the cards in a
"pretty" format. The cardValue function returns the value of a card and the
printhand function calls the printcard function to print out the hand. The
getbestscore function finds the best possible score of a hand while also being
aware of Aces. The main function uses a while loop to replay the game over and
over. I also use two other while loops to loop the "hit or stay" statement and
whether or not the dealers hand is worth 17 or more. After that while loop I
compare the value of the player hand and dealer hand to determine who is the
winner. The program then asks the player whether they want to play again
or not. */

#include <iostream>
#include <cstdlib>

using namespace std;

/* Prototypes */
void shuffle(int cards[]);
void printCard(int id);
int cardValue(int id);
void printHand(int hand[], int numCards);
int getBestScore(int hand[], int numCards);

const int NUM_CARDS = 52;

const char suit[4] = {'H','S','D','C'};
const char* type[13] =
  {"2","3","4","5","6","7",
   "8","9","10","J","Q","K","A"};
const int value[13] = {2,3,4,5,6,7,8,9,10,10,10,10,11};

void shuffle(int cards[])
{
  for (int i = 0; i < 52; i++)
    {
      cards[i] = i; //initialize cards
    }
  for (int i = 51; i > 0; i--)
    {
      int j = rand() % (i+1); //range from 1 to i
      int temp = cards[i]; //use temp to swap the value of
      cards[i] = cards[j]; //cards[i] and cards[j]
      cards[j] = temp;
    }
}

void printCard(int id)
{
  if (id >= 0 && id <= 12) //for hearts
    {
      if (id >= 0 && id <= 8) //for non-face/ace cards
        {
          cout << id+2 << "-" << "H" << " "; //id is 2 less than the value of
        }                                 //its respective card (i.e id 0 is 2)
      else if (id == 9) //for jack of hearts
        {
          cout << "J-H" << " ";
        }
      else if (id == 10)//for queen of hearts
        {
          cout << "Q-H" << " ";
        }
      else if (id == 11)//for king of hearts
        {
          cout << "K-H" << " ";
        }
      else //for ace of hearts
        {
          cout << "A-H" << " ";
        }
    }
  else if (id >= 13 && id <= 25) //for spades
    {
      if (id >= 13 && id <= 21) //for non-face/ace cards
        {
          cout << id-11 << "-" << "S" << " "; //id is 11 more than its
        }                             //respective value (i.e id 13 is 2)
      else if (id == 22) //for jack of spades
        {
          cout << "J-S" << " ";
        }
      else if (id == 23) //for queen of spades
        {
          cout << "Q-S" << " ";
        }
      else if (id == 24) //for king of spades
        {
          cout << "K-S" << " ";
        }
      else //for ace of spades
        {
          cout << "A-S" << " ";
        }
    }
    else if (id >= 26 && id <= 38) //for diamonds
      {
        if (id >= 26 && id <= 34) //for non-face/ace cards
          {
            cout << id-24 << "-" << "D" << " "; //id is 24 more than its
          }                             //respective value (i.e id 26 is 2)
        else if (id == 35) //for jack of diamonds
          {
            cout << "J-D" << " ";
          }
        else if (id == 36) //for queen of diamonds
          {
            cout << "Q-D" << " ";
          }
        else if (id == 37) //for king of diamonds
          {
            cout << "K-D" << " ";
          }
        else //for ace of diamonds
          {
            cout << "A-D" << " ";
          }
      }
    else //for clubs
      {
        if (id >= 39 && id <= 47) //for non-face/ace cards
          {
            cout << id-37 << "-" << "C" << " "; //id is 37 more than its
          }                             //respective value (i.e id 39 is 2)
        else if (id == 48) //for jack of clubs
          {
            cout << "J-C" << " ";
          }
        else if (id == 49) //for queen of clubs
          {
            cout << "Q-C" << " ";
          }
        else if (id == 50) //for king of clubs
          {
            cout << "K-C" << " ";
          }
        else //for ace of clubs
          {
            cout << "A-C" << " ";
          }
      }
}

int cardValue(int id)
{
  /******** You complete ****************/
  int value2[52] = {2,3,4,5,6,7,8,9,10,10,10,10,11,
  2,3,4,5,6,7,8,9,10,10,10,10,11,
  2,3,4,5,6,7,8,9,10,10,10,10,11,
  2,3,4,5,6,7,8,9,10,10,10,10,11}; //array representing all 52 values

  int val = value2[id];
  return val;
}

void printHand(int hand[], int numCards)
{
  for (int i = 0; i < numCards; i++) //loop to traverse array
    {                                //and print each card in hand
      printCard(hand[i]);
    }
}

int getBestScore(int hand[], int numCards)
{
  int bestScore = 0;
  for (int i = 0; i < numCards; i++)
    {
      bestScore = cardValue(hand[i]) + bestScore; //best score prior to
    }                                             //accounting for Aces
  if (bestScore <= 21) //if less than 21, no need to change value of Ace
    {
      return bestScore;
    }
  else //if greater than 21, change value of Ace from 11 to 1
    {
      for (int i = 0; i < numCards; i++) //searches every card in hand
        {
          if (cardValue(hand[i]) == 11) //finds an Ace
            {
              //changing value of Ace is like taking 10 off final score
              bestScore = bestScore - 10;
              //if score is under 21, return score, otherwise search for
              //another Ace to change value and get under 21
              if (bestScore <= 21)
                {
                  return bestScore;
                }
            }
        }
      return bestScore;
    }
}

int main(int argc, char* argv[])
{
 if(argc < 2){
    cout << "Error - Please provide the seed value." << endl;
    return 1;
  }
  int seed = atoi(argv[1]);
  srand(seed);

  int cards[52];
  int dhand[9];
  int phand[9];

  bool playagain = true; //variable used for playing again
  //while loop to determine whether player wants to play again
  while (playagain == true)
    {
      shuffle(cards);
      phand[0] = cards[0];
      phand[1] = cards[2];
      dhand[0] = cards[1];
      dhand[1] = cards[3];

      cout << "Dealer: " << "?" << " ";
      printCard(dhand[1]);
      cout << endl;
      cout << "Player: ";
      printHand(phand, 2);
      cout << endl;
      bool offrip21 = false;
      int numPcards = 2; //number of player cards
      int numDcards = 2; //number of dealer cards
      if (getBestScore(phand, numPcards) == 21 && getBestScore(dhand,numDcards) != 21)
        {
          cout << "Dealer: ";
          printHand(dhand, numDcards);
          cout << endl;
          cout << "Win " << 21 << " " << getBestScore(dhand, numDcards) << endl;
          offrip21 = true;
        }
      if (getBestScore(phand, numPcards) != 21 && getBestScore(dhand,numDcards) == 21)
        {
          cout << "Dealer: ";
          printHand(dhand, numDcards);
          cout << endl;
          cout << "Lose " << getBestScore(phand, numPcards) << " " << 21 << endl;
          offrip21 = true;
        }
      if (getBestScore(phand, numPcards) == 21 && getBestScore(dhand,numDcards) == 21) 
        {
          cout << "Dealer: ";
          printHand(dhand, numDcards);
          cout << endl;
          cout << "Push " << 21 << " " << 21;
          offrip21 = true;
        }       
      bool buststay = false; //if players busts or stays
      bool overorequal17 = false; //if dealer is equal too or over 17
      bool not21 = false;
      bool surrender = false;
      //if statement to make sure player wasn't dealt 21
      if (offrip21 == false)
        {
          not21 = true;
          //will continue to loop until player busts
          //or chooses to stay or hit 21
          while (buststay == false && not21 == true)
            {
              cout << "Type 'h' to hit, 's' to stay, 'd' to double down, and 'u' to surrender" << endl;
              char choice;
              cin >> choice;
              if (choice == 'h' && numPcards <= 9) //chooses to hit
                {
                  phand[numPcards] = cards[numPcards+2];
                  numPcards++;
                  cout << "Player: ";
                  printHand(phand, numPcards);
                  cout << endl;
                  //hits 21, leave the loop
                  if (getBestScore(phand, numPcards) == 21)
                    {
                      not21 = false;
                    }
                  //busts, leave the loop
                  if (getBestScore(phand, numPcards) > 21)
                    {
                      cout << "Player busts" << endl;
                      cout << "Lose " << getBestScore(phand, numPcards)
                      << " " << getBestScore(dhand, numDcards) << endl;
                      buststay = true;
                    }
                }
              else if (choice == 's') //chooses to stay, leave the loop
                {
                  buststay = true;
                }
              else if (choice == 'd') //choose to double down
                {
                  phand[numPcards] = cards[numPcards+2];
                  numPcards++;
                  cout << "Player: ";
                  printHand(phand, numPcards);
                  cout << endl;
                  //hits 21, leave the loop
                  if (getBestScore(phand, numPcards) == 21)
                    {
                      not21 = false;
                    }
                  //busts, leave the loop
                  else if (getBestScore(phand, numPcards) > 21)
                    {
                      cout << "Player busts" << endl;
                      cout << "Lose " << getBestScore(phand, numPcards)
                      << " " << getBestScore(dhand, numDcards) << endl;
                      buststay = true;
                    }
                  else
                    {
                      buststay = true;
                    }
                }                 
              else //chooses to surrender
                {
                  buststay = true;
                  surrender = true;
                  cout << "Dealer: ";
                  printHand(dhand, numDcards);
                  cout << endl;
                  cout << "Lose " << getBestScore(phand, numPcards) << " " <<getBestScore(dhand, numDcards);
                }
            }
        }
      //if player hasn't busted
      if (getBestScore(phand, numPcards) <= 21 && surrender == false && offrip21 == false)
        {
          int pcards = numPcards;
          //loop forces dealer to hit until 17 or higher
          while (overorequal17 == false)
            {
              {
                //if dealer is under 17, gives dealer another card
                if (getBestScore(dhand, numDcards) < 17 && numDcards < 9)
                  {
                    dhand[numDcards] = cards[pcards+2];
                    numDcards++;
                    pcards++;
                  }
                //if dealer is at 17 or more, leaves the loop
                else
                  {
                    overorequal17 = true;
                    cout << "Dealer: ";
                    printHand(dhand, numDcards);
                  }
              }
            }
        }
      //if players hand is greater than dealers and both under 21
      if (getBestScore(phand, numPcards) > getBestScore(dhand, numDcards)
      && getBestScore(phand, numPcards) <= 21 && surrender == false && offrip21 == false)
        {
          cout << endl;
          cout << "Win " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards);
        }
      //if players hand is less than dealers and both under 21
      if (getBestScore(phand, numPcards) < getBestScore(dhand, numDcards)
      && getBestScore(dhand, numDcards) <= 21 && surrender == false && offrip21 == false)
        {
          cout << endl;
          cout << "Lose " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards);
        }
      //if dealer busts
      if (getBestScore(dhand, numDcards) > 21 && surrender == false && offrip21 == false) 
        {
          cout << endl;
          cout << "Dealer busts" << endl;
          cout << "Win " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards);
        }
      //if value of both hands is equal (impossible for both to bust)
      //if player busts, dealer doesn't draw, so don't need <= 21 in statement
      if (getBestScore(phand, numPcards) == getBestScore(dhand, numDcards)
      && surrender == false && offrip21 == false)
        {
          cout << endl;
          cout << "Push " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards);
        }
        
      cout << endl;
      cout << endl;
      cout << "Play again? [y/n]" << endl;
      char yn;
      cin >> yn; //user inputs 'y' or 'n' to play again
      if (yn == 'y') //if 'y', will loop back to the first while loop in main
        {
          playagain = true;
        }
      else //if user inputs anything else, will end the program
        {
          return 0;
        }
    }

  return 0;
}

