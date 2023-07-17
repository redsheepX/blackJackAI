# Reward
# -profit point
# -超過21點 -profit*1.1

#Action
# [1,0,0,0] H(Hit)
# [0,1,0,0] S(Stand)
# [0,0,1,0] D(Double) 
# [0,0,0,1] P(Split) 


#State
#[Point,HasA,CardLen,BankerCard,mySdMul]

import torch
import random
import numpy as np
from collections import deque
from AIModel import QTrainer,BlackjackModule


MAX_MEMORY = 100_000
BATCH_SIZE = 100
LR = 0.001

class Agent:
    def __init__(self) -> None:
        pass


    def initData(self):
        self.epsilon = 0 #random
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = BlackjackModule(213,256,4)
        # import os
        # if os.path.exists('model/model.pth'):
        #     self.model.load_state_dict(torch.load('model/model.pth'))
        #     self.model.eval()
        #     self.epsilon = -100
            
        self.trainer = QTrainer(self.model,lr=LR,gamma=self.gamma)

    
    def get_state(self,StateDict:dict):
        state=[]
        for i in StateDict:
            for j in StateDict[i]:
                state.append(StateDict[i][j])
        return state

    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory,BATCH_SIZE)
        else:
            mini_sample = self.memory

        state,action,reward,next_state,done = zip(*mini_sample)
        self.trainer.train_step(state,action,reward,next_state,done)

    
    def train_short_memory(self,state,action,reward,next_state,done):
        self.trainer.train_step(state,action,reward,next_state,done)

    
    def get_action(self,state,n_games):
        # random moves: tradeoff exploration / exploitation
        if random.randint(0,200) < self.epsilon - n_games:
            move = random.randint(0,3)
        else:
            state0 = torch.tensor(state,dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
        return move

                
            
        
    
    
    
class GAME:
    pass

if __name__ == "__manin__":
    # train()
    a=Agent().countPoint([13])
    print(a)