from torch import nn
# from lib.non_local_concatenation import NONLocalBlock2D
# from lib.non_local_gaussian import NONLocalBlock2D
from lib.non_local_embedded_gaussian import NONLocalBlock2D
# from lib.non_local_dot_product import NONLocalBlock2D
import ipdb

class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()

#        self.convs = nn.Sequential(
#            #nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, stride=1, padding=1),
#            nn.Conv3d(in_channels=3, out_channels=64, kernel_size=(1,7,7),stride=(2,2,2),padding=1),
#	    nn.BatchNorm3d(64),
#            nn.ReLU(),
#	    nn.MaxPool3d(kernel_size=(3,3,3),stride=(2,2,2)),
#	  
#	    # 4x28x28
#            nn.Conv3d(in_channels=64, out_channels=128, kernel_size=(1,3,3),stride=(2,2,2),padding=1),
#	    nn.BatchNorm3d(128),
#            nn.ReLU(),
#	    # 2x28x28
#	    nn.MaxPool3d(kernel_size=(3,1,1),stride=(2,1,1)),
#	    
#            nn.Conv3d(in_channels=128, out_channels=256, kernel_size=(1,3,3),stride=(2,2,2),padding=1),
#	    nn.BatchNorm3d(256),
#            nn.ReLU(),
#	    # 1x7x7
#	    nn.MaxPool3d(kernel_size=(1,3,3),stride=(1,2,2)),
#	    
#	  )
#        self.fc = nn.Sequential(
#	    nn.Linear(in_features=256*7*7,out_features=400),
#	    nn.ReLU(),
#	    nn.Dropout(0.5),
#	  )
#
            #nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, stride=1, padding=1),
        self.conv1 = nn.Conv3d(in_channels=3, out_channels=64, kernel_size=(1,7,7),stride=(2,2,2),padding=(0,3,3))
        self.bn1 = nn.BatchNorm3d(64)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool3d(kernel_size=(3,3,3),stride=(2,2,2),padding=(1,1,1))
      
	# 4x28x28
        self.conv2 = nn.Conv3d(in_channels=64, out_channels=128, kernel_size=(1,3,3),stride=(2,2,2),padding=(0,1,1))
        self.bn2 = nn.BatchNorm3d(128)
        self.relu2 = nn.ReLU()
	# 2x28x28
        self.pool2 = nn.MaxPool3d(kernel_size=(3,1,1),stride=(2,1,1),padding=(1,0,0))
	
	#1x14x14
        self.conv3 = nn.Conv3d(in_channels=128, out_channels=256, kernel_size=(1,3,3),stride=(2,2,2),padding=(0,1,1))
        self.bn3 = nn.BatchNorm3d(256)
        self.relu3 = nn.ReLU()

	# 1x4x4
        self.pool3 = nn.MaxPool3d(kernel_size=(1,7,7),stride=(1,2,2),padding=(0,0,0))
	
        self.linear = nn.Linear(in_features=256*4*4,out_features=400)
      
        self.relu4 = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
	  
    def forward(self, x):
        batch_size = x.size(0)
        #output = self.convs(x).view(batch_size, -1)
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.pool2(x)

        
        x = self.conv3(x)
        
        x = self.bn3(x)
        x = self.relu3(x)
        x = self.pool3(x).view(batch_size,-1) 
        
        x = self.linear(x)
        x = self.relu4(x)
        x = self.dropout(x)
        
        return x
	#output = self.convs(x)

        #print (output.size())
        #ipdb.set_trace()
        #output = self.fc(output)
        #return output

class Bottleneck(nn.Module):
    expansion = 4
    def __init__(self,inplanes,planes,stride=1,downsample=None):
        super(Bottleneck,self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False )
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias = False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes*4,kernel_size=1,bias=False)
        self.bn3 = nn.BatchNorm2d(planes*4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self,x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        
        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)
        
        out += residual
        out = self.relu(out)
        return out

class ResNet(nn.Module):
    def __init__(self,block,layers,num_classes=400):
        self.inplanes = 64
        super(ResNet, self).__init__()
        self.conv1 = nn.Conv2d(3,64,kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block,64,layers[0])
        self.layer2 = self._make_layer(block,128,layers[1],stride=2)
        self.layer3 = self._make_layer(block,256,layers[2],stride=2)
        self.layer4 = self._make_layer(block,512,layers[3],stride=2)
        self.avgpool = nn.AvgPool2d(7, stride=1)
        self.fc = nn.Linear(512*block.expansion,num_classes)

    def _make_layer(self,block,planes,blocks,stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes*block.expansion:
            downsample = nn.Sequential (
                nn.Conv2d(self.inplanes,planes * block.expansion ,
                kernel_size = 1, stride = stride ,bias = False),
                nn.BatchNorm2d(planes * block.expansion),
                )
        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion 
        for i in range(1,blocks):
            layers.append(block(self.inplanes,planes))
        return nn.Sequential(*layers)

    def forward(self,x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        print (x.shape)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = x.view(x.size(0),-1)
        x = self.fc(x)

        return x

    def resnet50(pretrained=False, **kwargs):
        model = ResNet(Bottleneck, [3,4,6,3], **kwargs)
        return model

if __name__ == '__main__':
    import torch
    from torch.autograd import Variable
    img = Variable(torch.randn(1,3,224, 224))
    net = ResNet.resnet50()
    out = net(img)
    print(out.size())

