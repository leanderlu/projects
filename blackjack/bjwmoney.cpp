//Created by Leander Lu

#include <iostream>
#include <cstdlib>
#include <cmath>
#include <iomanip>



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
 /*if(argc < 2){
    cout << "Error - Please provide the seed value." << endl;
    return 1;
  }*/
  //int seed = atoi(argv[1]);
  srand(time(0));

  int cards[52];
  int dhand[9];
  int phand[9];
  int phand2[9];
  double amount;
  double money = 0;

  bool playagain = true; //variable used for playing again
  //while loop to determine whether player wants to play again
  while (playagain == true)
    {
      bool error = true;
      while (error == true)
      {
        cout << "How much do you want to bet? ($1.00 - $5,000.00) " << endl;
        cin >> amount;
        if (amount > 5000)
          {
            cout << "Error - amount is too high, please try again with a smaller amount" << endl;
          }
        else if (amount < 1)
          {
            cout << "Error - amount is too low, please try again with a larger amount" << endl;
          }
        else
          {
            error = false;
          }
      }
      double amount2 = amount;
      money -= amount;
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
      int numP2cards = 0; //for splits
      int numDcards = 2; //number of dealer cards
      if (getBestScore(phand, numPcards) == 21 && getBestScore(dhand,numDcards) != 21)
        {
          cout << "Dealer: ";
          printHand(dhand, numDcards);
          cout << endl;
          cout << "Win " << 21 << " " << getBestScore(dhand, numDcards) << endl;
          offrip21 = true;
          money += (amount*2);
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
          money += amount;
        }       
      bool diddoubledown = false; //if they double down;
      bool buststay = false; //if players busts or stays
      bool overorequal17 = false; //if dealer is equal too or over 17
      bool not21 = false;
      bool surrender = false;
      int split = 1;
      bool candoubledown = true;
      int x = numPcards;
      //if statement to make sure player wasn't dealt 21
      if (offrip21 == false)
        {
        while (split == 1 || split == 2)
          {
          not21 = true;
          split = 0;
          //will continue to loop until player busts
          //or chooses to stay or hit 21
          while (buststay == false && not21 == true)
            {
              if (split == 0 && candoubledown == true) 
              {
                cout << "Type 'h' to hit, 's' to stay, 'p' to split, d' to double down, and 'u' to surrender" << endl;
              }
              if (split == 1 && candoubledown == true)
              {
                cout << "For Hand 1, type 'h' to hit, 's' to stay, and 'd' to double down" << endl;
              }
              if (split == 2 && numP2cards == 1)
              {
                cout << "Hand 2: ";
                printHand(phand2, numP2cards);
                cout << endl;
                cout << "For Hand 2, type 'h' to hit, 's' to stay, and 'd' to double down" << endl;
              }
              if (split == 0 && candoubledown == false)
              {
                cout << "Type 'h' to hit and 's' to stay" << endl;
              }
              if (split == 1 && candoubledown == false)
              {
                cout << "For Hand 1, type 'h' to hit and 's' to stay" << endl;
              }
              if (split == 2 && numP2cards >1)
              {
                cout << "For Hand 2, type 'h' to hit and 's' to stay" << endl;
              }
              char choice;
              cin >> choice;
              if (choice == 'h' && numPcards <= 9) //chooses to hit
                {
                 if (split == 0)
                  {
                  candoubledown = false;
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
                      cout << "Player Busts" << endl;
                      cout << "Lose " << getBestScore(phand, numPcards)
                      << " " << getBestScore(dhand, numDcards) << endl;
                      buststay = true;
                    }
                  }
                  else if (split == 1)
                    {
                       candoubledown = false;
                       phand[numPcards] = cards[numPcards+3];
                       numPcards++;
                       cout << "Player Hand 1: ";
                       printHand(phand, numPcards);
                       cout << endl;
                       if (getBestScore(phand, numPcards) == 21)
                        {
                          cout << "Player Hand 1 Value: 21" << endl;
                          split = 2;
                        }
                      if (getBestScore(phand, numPcards) > 21)
                        {
                          cout << "Player Hand 1 Busts with " << getBestScore(phand, numPcards) << endl;
                          split = 2;
                        }
                    }
                  else
                    {
                      candoubledown = false;
                      phand2[numP2cards] = cards[x+3];
                      numP2cards++;
                      x++;
                      cout << "Player Hand 2: ";
                      printHand(phand2, numP2cards);
                      cout << endl;
                      if (getBestScore(phand2, numP2cards) == 21)
                        {
                          cout << "Player Hand 2 Value: 21" << endl;
                          split = 3;
                          buststay = true;
                        }
                      if (getBestScore(phand2, numP2cards) > 21)
                        {
                          split = 3;
                          buststay = true;
                          cout << "Player Hand 2 Busts with " << getBestScore(phand2, numP2cards) << endl;
                        }
                    }
                }
              else if (choice == 's') //chooses to stay, leave the loop
                { 
                  if (split == 0)
                  {
                    cout << "Player Hand Value: " << getBestScore(phand, numPcards) << endl;
                    buststay = true;
                  }
                  else if (split == 1)
                  {
                    cout << "Player Hand 1 Value: " << getBestScore(phand, numPcards) << endl;
                    split = 2;
                  }
                  else
                  {
                    cout << "Player Hand 2 Value: " << getBestScore(phand2, numP2cards) << endl;
                    split = 3;
                    buststay = true;
                  }
                }
              else if (choice == 'p') //chooses to split
                {
                  split = 1;
                  money -= amount;
                  phand2[0] = phand[1];
                  phand[1] = NULL;
                  numPcards = numPcards/2;
                  numP2cards++;
                  cout << "Player Hand 1: ";
                  printHand(phand, numPcards);
                  cout << endl;
                  cout << "Player Hand 2: ";
                  printHand(phand2, numP2cards);        
                  cout << endl;
                }
              else if (choice == 'd') //choose to double down
                {
                  diddoubledown = true;
                  if (split == 0)
                  {
                  money -= amount;
                  amount *= 2;
                  candoubledown = false;
                  phand[numPcards] = cards[numPcards+2];
                  numPcards++;
                  cout << "Player: ";
                  printHand(phand, numPcards);
                  cout << endl;
                  //hits 21, leave the loop
                  if (getBestScore(phand, numPcards) == 21)
                    {
                      cout << "Player Hand Value: 21" << endl;
                      not21 = false;
                    }
                  //busts, leave the loop
                  else if (getBestScore(phand, numPcards) > 21)
                    {
                      cout << "Player Busts" << endl;
                      cout << "Lose " << getBestScore(phand, numPcards)
                      << " " << getBestScore(dhand, numDcards) << endl;
                      buststay = true;
                      money += (amount*2);
                    }
                  else
                    {
                      buststay = true;
                    }
                  }
                  //choose to double down hand 1 of a split
                  else if (split == 1)
                  {
                  money -= amount;
                  amount *= 2;
                  phand[numPcards] = cards[numPcards+3];
                  numPcards++;
                  cout << "Hand 1: ";
                  printHand(phand, numPcards);
                  cout << endl;
                  //hits 21, leave the loop
                  if (getBestScore(phand, numPcards) == 21)
                    {
                      cout << "Player Hand 1 Value: 21" << endl;
                      split = 2;
                    }
                  //busts, leave the loop
                  else if (getBestScore(phand, numPcards) > 21)
                    {
                      cout << "Player Hand 1 Busts with " << getBestScore(phand, numPcards) << endl;
                      split = 2;
                    }
                  else
                    {
                      split = 2;
                    }
                  }
                  //choose to double down hand 2 of a split
                  else
                  {
                  int x = numPcards;
                  phand2[numP2cards] = cards[x+3];
                  numP2cards++;
                  x++;
                  cout << "Player Hand 2: ";
                  printHand(phand2, numP2cards);
                  cout << endl;
                  //hits 21, leave the loop
                  if (getBestScore(phand2, numP2cards) == 21)
                    {
                      cout << "Player Hand 2 Value: 21" << endl;
                      not21 = false;
                      split = 3;
                    }
                  //busts, leave the loop
                  else if (getBestScore(phand2, numP2cards) > 21)
                    {
                      cout << "Player Hand 2 Busts with " << getBestScore(phand, numPcards) << endl;
                      buststay = true;
                      split = 3;
                    }
                  else
                    {
                      split = 3;
                      buststay = true;
                    }
                  }
                }                 
              else //chooses to surrender
                {
                  money += (amount/2);
                  buststay = true;
                  surrender = true;
                  cout << "Dealer Hand Value: ";
                  printHand(dhand, numDcards);
                  cout << endl;
                  cout << "Lose " << getBestScore(phand, numPcards) << " " <<getBestScore(dhand, numDcards);
                }
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
                    cout << "Dealer Hand Value: ";
                    printHand(dhand, numDcards);
                  }
              }
            }
        }
      if (offrip21 == false && surrender == false && diddoubledown == false)
      {
      //if players hand is greater than dealers and both under 21
      if (split == 0)
      {
      if (getBestScore(phand, numPcards) > getBestScore(dhand, numDcards)
      && getBestScore(phand, numPcards) <= 21)
        {
          cout << endl;
          cout << "Win " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //if players hand is less than dealers and both under 21
      if (getBestScore(phand, numPcards) < getBestScore(dhand, numDcards)
      && getBestScore(dhand, numDcards) <= 21)
        {
          cout << endl;
          cout << "Lose " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
        }
      //if dealer busts
      if (getBestScore(dhand, numDcards) > 21) 
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Win " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //if value of both hands is equal (impossible for both to bust)
      //if player busts, dealer doesn't draw, so don't need <= 21 in statement
      if (getBestScore(phand, numPcards) == getBestScore(dhand, numDcards))
        {
          cout << endl;
          cout << "Push " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += (amount);
        }
      }
      if (split == 3) //if a split occurred
      {
      //compares hand 1 to dealer
      if (getBestScore(phand, numPcards) > getBestScore(dhand, numDcards)
      && getBestScore(phand, numPcards) <= 21)
        {
          cout << endl;
          cout << "Hand 1 Wins " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //compares hand 2 to dealer
      if (getBestScore(phand2, numP2cards) > getBestScore(dhand, numDcards)
      && getBestScore(phand2, numP2cards) <= 21)
      {
        cout << endl;
        cout << "Hand 2 Wins " << getBestScore(phand2, numP2cards) << " "
        << getBestScore(dhand, numDcards) << endl;
        money += (amount2*2);
      }
      //compares hand 1 to dealer
      if (getBestScore(phand, numPcards) < getBestScore(dhand, numDcards)
      && getBestScore(dhand, numDcards) <= 21)
        {
          cout << endl;
          cout << "Hand 1 Loses " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
        }
      //compares hand 2 to dealer
      if (getBestScore(phand2, numP2cards) < getBestScore(dhand, numDcards)
      && getBestScore(dhand, numDcards) <= 21)
        {
          cout << endl;
          cout << "Hand 2 Loses " << getBestScore(phand2, numP2cards) << " "
          << getBestScore(dhand, numDcards) << endl;
        }
      if (getBestScore(phand, numPcards) > 21 && getBestScore(phand2, numP2cards) > 21)
        {
          cout << endl;
          cout << "Both Hands Bust" << endl;
          cout << "You Fucking Suck" << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards) << endl;
          cout << "Hand 2: " << getBestScore (phand2, numP2cards) << endl;
          cout << "Dealer: " << getBestScore (dhand, 2) << endl;
          cout << "Fucking Donut" << endl;
        }
      
      //if dealer busts
      if (getBestScore(dhand, numDcards) > 21 && getBestScore(phand, numPcards) <= 21 && getBestScore(phand2, numP2cards) <= 21) 
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Both Hands Win " << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          cout << "Hand 2: " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += ((amount*2) + (amount2*2));
        }
      //if dealer and hand 1 bust
      if (getBestScore(dhand, numDcards) > 21 && getBestScore(phand, numPcards) > 21 && getBestScore(phand2, numP2cards) <= 21)
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Hand 1 Busts, Hand 2 Wins" << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          cout << "Hand 2: " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += (amount2*2);
        }
      //if dealer and hand 2 bust
      if (getBestScore(dhand, numDcards) > 21 && getBestScore(phand, numPcards) <= 21 && getBestScore(phand2, numP2cards) > 21)
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Hand 1 Wins, Hand 2 Busts" << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          cout << "Hand 2: " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //if hand 1 pushes
      if (getBestScore(phand, numPcards) == getBestScore(dhand, numDcards))
        {
          cout << endl;
          cout << "Hand 1 Pushes " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += amount;
        }
      //if hand 2 pushes
      if (getBestScore(phand2, numP2cards) == getBestScore(dhand, numDcards))
        {
          cout << endl;
          cout << "Hand 2 Pushes " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += amount2;
        }
      }
      }
    if (offrip21 == false && surrender == false && diddoubledown == true)
    {
      if (split == 0)
      {
      if (getBestScore(phand, numPcards) > getBestScore(dhand, numDcards)
      && getBestScore(phand, numPcards) <= 21)
        {
          cout << endl;
          cout << "Win " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //if players hand is less than dealers and both under 21
      if (getBestScore(phand, numPcards) < getBestScore(dhand, numDcards)
      && getBestScore(dhand, numDcards) <= 21)
        {
          cout << endl;
          cout << "Lose " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
        }
      //if dealer busts
      if (getBestScore(dhand, numDcards) > 21) 
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Win " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //if value of both hands is equal (impossible for both to bust)
      //if player busts, dealer doesn't draw, so don't need <= 21 in statement
      if (getBestScore(phand, numPcards) == getBestScore(dhand, numDcards))
        {
          cout << endl;
          cout << "Push " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += amount;
        }
      }
      if (split == 3) //if a split occurred
      {
      //compares hand 1 to dealer
      if (getBestScore(phand, numPcards) > getBestScore(dhand, numDcards)
      && getBestScore(phand, numPcards) <= 21)
        {
          cout << endl;
          cout << "Hand 1 Wins " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //compares hand 2 to dealer
      if (getBestScore(phand2, numP2cards) > getBestScore(dhand, numDcards)
      && getBestScore(phand2, numP2cards) <= 21)
      {
        cout << endl;
        cout << "Hand 2 Wins " << getBestScore(phand2, numP2cards) << " "
        << getBestScore(dhand, numDcards) << endl;
        money += (amount2*2);
      }
      //compares hand 1 to dealer
      if (getBestScore(phand, numPcards) < getBestScore(dhand, numDcards)
      && getBestScore(dhand, numDcards) <= 21)
        {
          cout << endl;
          cout << "Hand 1 Loses " << getBestScore(phand, numPcards) << " "
          << getBestScore(dhand, numDcards) << endl;
        }
      //compares hand 2 to dealer
      if (getBestScore(phand2, numP2cards) < getBestScore(dhand, numDcards)
      && getBestScore(dhand, numDcards) <= 21)
        {
          cout << endl;
          cout << "Hand 2 Loses " << getBestScore(phand2, numP2cards) << " "
          << getBestScore(dhand, numDcards) << endl;
        }
      if (getBestScore(phand, numPcards) > 21 && getBestScore(phand2, numP2cards) > 21)
        {
          cout << endl;
          cout << "Both Hands Bust" << endl;
          cout << "You Fucking Suck" << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards) << endl;
          cout << "Hand 2: " << getBestScore (phand2, numP2cards) << endl;
          cout << "Dealer: " << getBestScore (dhand, 2) << endl;
          cout << "Fucking Donut" << endl;
        }
      
      //if dealer busts
      if (getBestScore(dhand, numDcards) > 21 && getBestScore(phand, numPcards) <= 21 && getBestScore(phand2, numP2cards) <= 21) 
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Both Hands Win " << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          cout << "Hand 2: " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += ((amount*2) + (amount2*2));
        }
      //if dealer and hand 1 bust
      if (getBestScore(dhand, numDcards) > 21 && getBestScore(phand, numPcards) > 21 && getBestScore(phand2, numP2cards) <= 21)
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Hand 1 Busts, Hand 2 Wins" << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          cout << "Hand 2: " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += (amount2*2);
        }
      //if dealer and hand 2 bust
      if (getBestScore(dhand, numDcards) > 21 && getBestScore(phand, numPcards) <= 21 && getBestScore(phand2, numP2cards) > 21)
        {
          cout << endl;
          cout << "Dealer Busts" << endl;
          cout << "Hand 1 Wins, Hand 2 Busts" << endl;
          cout << "Hand 1: " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          cout << "Hand 2: " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += (amount*2);
        }
      //if hand 1 pushes
      if (getBestScore(phand, numPcards) == getBestScore(dhand, numDcards))
        {
          cout << endl;
          cout << "Hand 1 Pushes " << getBestScore(phand, numPcards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += amount;
        }
      //if hand 2 pushes
      if (getBestScore(phand2, numP2cards) == getBestScore(dhand, numDcards))
        {
          cout << endl;
          cout << "Hand 2 Pushes " << getBestScore(phand2, numP2cards)
          << " " << getBestScore(dhand, numDcards) << endl;
          money += amount2;
        }
      }
    }
      cout << endl;
      cout << "Play Again? [y/n]" << endl;
      char yn;
      cin >> yn; //user inputs 'y' or 'n' to play again
      if (yn == 'y') //if 'y', will loop back to the first while loop in main
        {
          playagain = true;
        }
      else //if user inputs anything else, will end the program
        {
          cout << setprecision(2) << fixed;
          cout << "$" << money << endl;
          return 0;
        }
    } 

  return 0;
}

