import torch
import torchvision
import sys
import os
from torch.utils.data import DataLoader

sys.path.append(os.getcwd())
from unimodals.common_models import MLP
r3d = torchvision.models.video.r3d_18(pretrained=True)
model=torch.nn.Sequential(r3d,MLP(400,200,5)).cuda()
optim = torch.optim.Adam(model.parameters(),lr=0.0001)
datas = torch.load('/data/yiwei/kinetics_small/valid/batch0.pkt')
epochs = 15
valid_dataloader = DataLoader(datas,shuffle=False,batch_size=5)
bestvaloss=1000
criterion = torch.nn.CrossEntropyLoss()
#a=input()
for ep in range(epochs):
    totalloss = 0.0
    total=0
    for i in range(24):
        print("epoch "+str(ep)+" subiter "+str(i))
        datas = torch.load('/data/yiwei/kinetics_small/train/batch'+str(i)+'.pkt')
        train_dataloader = DataLoader(datas,shuffle=True,batch_size=5)
        for j in train_dataloader:
            optim.zero_grad()
            out = model(j[0].cuda())
            #print(out)
            loss = criterion(out,j[1].cuda())
            loss.backward()
            optim.step()
            totalloss += loss*len(j[0])
            total += len(j[0])
    print("Epoch "+str(ep)+" train loss: "+str(totalloss/total))
    with torch.no_grad():
        total = 0
        correct = 0
        totalloss = 0.0
        for j in valid_dataloader:
            out = model(j[0].cuda())            
            loss = criterion(out,j[1].cuda())
            totalloss += loss
            for ii in range(len(out)):
                total += 1
                if out[ii].tolist().index(max(out[ii]))==j[1][ii]:
                    correct += 1
        valoss = totalloss/total
        print("Valid loss: "+str(totalloss/total)+" acc: "+str(float(correct)/total))
        if valoss < bestvaloss:
            print("Saving best")
            bestvaloss = valoss
            torch.save(model,'best.pt')

print('testing')
valid_dataloader=None
datas = torch.load('/data/yiwei/kinetics_small/test/batch0.pkt')
test_dataloader = DataLoader(datas,shuffle=False,batch_size=5)
with torch.no_grad():
    total = 0
    correct = 0
    totalloss = 0.0
    for j in test_dataloader:
        out = model(j[0].cuda())
        loss = criterion(out,j[1].cuda())
        totalloss += loss
        for ii in range(len(out)):
            total += 1
            if out[ii].tolist().index(max(out[ii]))==j[1][ii]:
                correct += 1
    print("Test loss: "+str(totalloss/total)+" acc: "+str(float(correct)/total))


    
