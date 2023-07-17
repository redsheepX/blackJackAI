import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os


class BlackjackModule(nn.Module):
    def __init__(self, input_size,hidden_size,output_size):
        super(BlackjackModule, self).__init__()
        self.input_layer = nn.Linear(input_size, hidden_size)
        self.hidden_layer = nn.Linear(hidden_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, output_size)


    def forward(self, x):
        x_input=x.tolist()
        x = F.relu(self.input_layer(x))
        x = F.relu(self.hidden_layer(x))
        x = self.output_layer(x)
        if not self.canDouble(x_input):
            x[-2] = float('-inf')
        if not self.canSplit(x_input):
            x[-1] = float('-inf')

        return x

    def save(self,filename='BlackJack.pth'):
        model_folder_path = 'model/'
        if not os.path.exists(model_folder_path):
            os.mkdir(model_folder_path)
            
        filename = os.path.join(model_folder_path,filename)
        torch.save(self.state_dict(),filename)
        
    def canDouble(self,State:list):
        if type(State[0])==list:
            State=State[0]
        else:
            State=State
        cardLen=0
        canDouble=True
        for i in State[0:51]:
            cardLen += i
        if cardLen>2:
            canDouble=False
        return canDouble
    
    def canSplit(self,State:list):
        if type(State[0])==list:
            State=State[0]
        else:
            State=State
        canSplit=True
        cardList=[]
        for i in State[54:105]:
            if i >0:
                canSplit=False
                return canSplit
        for i in range(len(State[0:51])):
            if State[0:51][i] >0:
                for j in range(i):
                    cardList.append(i)
        #cardList數量>2 或 點數不相等
        if len(cardList)!=2 or (self.singleCardPoint(cardList[0]) != self.singleCardPoint(cardList[1])):
            canSplit=False
        return canSplit
            
    def singleCardPoint(self,card:int):
        while True:
            if card in [13,26,39,52]:
                return 11
            if card > 13:
                card  -= 13
            elif card < 9:
                return card+1
            elif card > 8 and card < 13:
                return 10
        
        
class QTrainer:
    def __init__(self,model:BlackjackModule,lr,gamma) -> None:
        self.lr=lr
        self.gamma=gamma
        self.model=model
        self.optimizer = optim.Adam(model.parameters(),lr=self.lr)
        self.criterion:nn.MSELoss = nn.MSELoss()

    def train_step(self,state,action,reward,next_state,done): 
        state= torch.tensor(state,dtype=torch.float)
        next_state= torch.tensor(next_state,dtype=torch.float)
        action= torch.tensor(action,dtype=torch.float)
        reward= torch.tensor(reward,dtype=torch.float)
        if len(state.shape) ==1:
            state = torch.unsqueeze(state,0)
            next_state = torch.unsqueeze(next_state,0)
            action = torch.unsqueeze(action,0)
            reward = torch.unsqueeze(reward,0)
            done = (done,)
        
        
        # 1: predicted Q values with current state
        pred = self.model(state)
        
        # 2:Q_new = r + y * MAX(next_predicted Q value)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            target[idx][torch.argmax(action[idx]).item()] = Q_new
                    
        self.optimizer.zero_grad()
        loss = self.criterion(target,pred)
        print(loss)
        loss.backward()
        
        self.optimizer.step()
        
