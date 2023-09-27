from datafree.models import classifiers, deeplab
from torchvision import datasets, transforms as T
from datafree.utils import sync_transforms as sT

from PIL import PngImagePlugin
LARGE_ENOUGH_NUMBER = 100
PngImagePlugin.MAX_TEXT_CHUNK = LARGE_ENOUGH_NUMBER * (1024**2)


import os
import torch
import torchvision
import datafree
import torch.nn as nn 
from PIL import Image
from datafree.datasets.smallimagenet import SmallImagenet

NORMALIZE_DICT = {
    'mnist':    dict( mean=(0.1307,),                std=(0.3081,) ),
    'cifar10':  dict( mean=(0.4914, 0.4822, 0.4465), std=(0.2023, 0.1994, 0.2010) ),
    'cifar100': dict( mean=(0.5071, 0.4867, 0.4408), std=(0.2675, 0.2565, 0.2761) ),
    'imagenet': dict( mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    'tinyimagenet': dict( mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    
    'cub200':   dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'stanford_dogs':   dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'stanford_cars':   dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'places365_32x32': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'places365_64x64': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'places365': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'svhn': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'tiny_imagenet': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'imagenet_32x32': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    
    # for semantic segmentation
    'camvid': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
    'nyuv2': dict( mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5) ),
}


MODEL_DICT = {
    # https://github.com/polo5/ZeroShotKnowledgeTransfer
    'wrn16_1': classifiers.wresnet.wrn_16_1,
    'wrn16_2': classifiers.wresnet.wrn_16_2,
    'wrn40_1': classifiers.wresnet.wrn_40_1,
    'wrn40_2': classifiers.wresnet.wrn_40_2,

    # https://github.com/HobbitLong/RepDistiller
    'resnet8': classifiers.resnet_tiny.resnet8,
    'resnet20': classifiers.resnet_tiny.resnet20,
    'resnet32': classifiers.resnet_tiny.resnet32,
    'resnet56': classifiers.resnet_tiny.resnet56,
    'resnet110': classifiers.resnet_tiny.resnet110,
    'resnet8x4': classifiers.resnet_tiny.resnet8x4,
    'resnet32x4': classifiers.resnet_tiny.resnet32x4,
    'vgg8': classifiers.vgg.vgg8_bn,
    'vgg11': classifiers.vgg.vgg11_bn,
    'vgg13': classifiers.vgg.vgg13_bn,
    'shufflenetv2': classifiers.shufflenetv2.shuffle_v2,
    'mobilenetv2': classifiers.mobilenetv2.mobilenet_v2,
    
    # https://github.com/huawei-noah/Data-Efficient-Model-Compression/tree/master/DAFL
    'resnet50':  classifiers.resnet.resnet50,
    'resnet18':  classifiers.resnet.resnet18,
    'resnet34':  classifiers.resnet.resnet34,
}

IMAGENET_MODEL_DICT = {
    'resnet50_imagenet': classifiers.resnet_in.resnet50,
    'resnet18_imagenet': classifiers.resnet_in.resnet18,
    'mobilenetv2_imagenet': torchvision.models.mobilenet_v2,
}

SEGMENTATION_MODEL_DICT = {
    'deeplabv3_resnet50':  deeplab.deeplabv3_resnet50,
    'deeplabv3_mobilenet': deeplab.deeplabv3_mobilenet,
}


def get_model(name: str, num_classes, pretrained=False, **kwargs):
    if 'imagenet' in name:
        model = IMAGENET_MODEL_DICT[name](pretrained=pretrained)
        if num_classes!=1000:
            model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif 'deeplab' in name:
        model = SEGMENTATION_MODEL_DICT[name](num_classes=num_classes, pretrained_backbone=kwargs.get('pretrained_backbone', False))
    else:
        print(name)
        model = MODEL_DICT[name](num_classes=num_classes)
    return model 


def get_dataset(name: str, data_root: str='data', return_transform=False, split=['A', 'B', 'C', 'D']):
    name = name.lower()
    data_root = os.path.expanduser( data_root )

    if name=='mnist':
        num_classes = 10
        train_transform = T.Compose([
            T.Resize((32, 32)),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])
        val_transform = T.Compose([
            T.Resize((32, 32)),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])      
        # data_root = os.path.join( data_root, 'torchdata' )
        train_dst = datasets.MNIST(data_root, train=True, download=True, transform=train_transform)
        val_dst = datasets.MNIST(data_root, train=False, download=True, transform=val_transform)
    elif name=='cifar10':
        num_classes = 10
        train_transform = T.Compose([
            T.RandomCrop(32, padding=4),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])
        data_root = os.path.join( data_root, 'CIFAR10' )
        train_dst = datasets.CIFAR10(data_root, train=True, download=True, transform=train_transform)
        val_dst = datasets.CIFAR10(data_root, train=False, download=True, transform=val_transform)
    elif name=='cifar100':
        num_classes = 100
        train_transform = T.Compose([
            T.RandomCrop(32, padding=4),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])
        data_root = os.path.join( data_root, 'CIFAR100' )
        train_dst = datasets.CIFAR100(data_root, train=True, download=True, transform=train_transform)
        val_dst = datasets.CIFAR100(data_root, train=False, download=True, transform=val_transform)
    elif name=='svhn':
        num_classes = 10
        train_transform = T.Compose([
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] ),
        ])
        # data_root = os.path.join( data_root, 'torchdata' )
        train_dst = datasets.SVHN(data_root, split='train', download=True, transform=train_transform)
        val_dst = datasets.SVHN(data_root, split='test', download=True, transform=val_transform)
    elif name=='imagenet' or name=='imagenet-0.5':
        num_classes=1000
        train_transform = T.Compose([
            T.RandomResizedCrop(224),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        val_transform = T.Compose([
            T.Resize(256),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        data_root = os.path.join(data_root, 'ImageNet')
        train_root = os.path.join(data_root, 'train')
        val_root = os.path.join(data_root, 'val')
        # train_dst = None
        train_dst = datasets.ImageFolder(root=val_root, transform=train_transform)
        val_dst = datasets.ImageFolder(root=val_root, transform=train_transform)
        # train_dst = datasets.ImageNet(data_root, split='train', transform=train_transform)
        # val_dst = datasets.ImageNet(data_root, split='val', transform=val_transform)
    elif name=='imagenet_32x32':
        num_classes=1000
        train_transform = T.Compose([
            T.RandomCrop(32, padding=4),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        data_root = os.path.join( data_root, 'ImageNet_32x32' ) 
        train_dst = datasets.ImageFolder(os.path.join(data_root, 'train'), transform=train_transform)
        val_dst = datasets.ImageFolder(os.path.join(data_root, 'val'), transform=val_transform)
    # if using official downloaded imagenet-32
    elif name == 'small_imagenet':
        num_classes = 1000
        train_transform = T.Compose([
            T.RandomCrop(32, padding=4),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT['imagenet_32x32']),
        ])
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT['imagenet_32x32']),
        ])
        train_dst = SmallImagenet(root=data_root, size=32, train=True, transform=train_transform, classes=range(1000))
        val_dst = SmallImagenet(root=data_root, size=32, train=False, transform=val_transform, classes=range(1000))
    elif name=='places365_32x32':
        num_classes=365
        train_transform = T.Compose([
            T.RandomCrop(32, padding=4),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        data_root = os.path.join( data_root, 'Places365_32x32' ) 
        train_dst = datasets.ImageFolder(os.path.join(data_root, 'train'), transform=train_transform)
        val_dst = datasets.ImageFolder(os.path.join(data_root, 'val'), transform=val_transform)
    elif name=='places365_64x64':
        num_classes=365
        train_transform = T.Compose([
            T.RandomCrop(64, padding=8),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        data_root = os.path.join( data_root, 'Places365_64x64' ) 
        train_dst = datasets.ImageFolder(os.path.join(data_root, 'train'), transform=train_transform)
        val_dst = None #datasets.ImageFolder(os.path.join(data_root, 'val'), transform=val_transform)
    elif name=='places365':
        num_classes=365
        train_transform = T.Compose([
            T.RandomResizedCrop(224),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        val_transform = T.Compose([
            T.Resize(256),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(**NORMALIZE_DICT[name]),
        ])
        data_root = os.path.join( data_root, 'Places365' ) 
        train_dst = datasets.ImageFolder(os.path.join(data_root, 'train'), transform=train_transform)
        val_dst = datasets.ImageFolder(os.path.join(data_root, 'val'), transform=val_transform)
    elif name=='cub200':
        num_classes=200
        train_transform = T.Compose([
            T.Resize(64),
            T.RandomCrop(64, padding=8),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )
        val_transform = T.Compose([
            T.Resize(64),
            T.CenterCrop(64),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )       
        data_root = os.path.join(data_root, 'CUB200')
        train_dst = datafree.datasets.CUB200(data_root, split='train', transform=train_transform)
        val_dst = datafree.datasets.CUB200(data_root, split='val', transform=val_transform)
    elif name=='stanford_dogs':
        num_classes=120
        train_transform = T.Compose([
            T.Resize(64),
            T.RandomCrop(64, padding=8),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )
        val_transform = T.Compose([
            T.Resize(64),
            T.CenterCrop(64),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )       
        data_root = os.path.join(data_root, 'StanfordDogs')
        train_dst = datafree.datasets.StanfordDogs(data_root, split='train', transform=train_transform)
        val_dst = datafree.datasets.StanfordDogs(data_root, split='test', transform=val_transform)
    elif name=='stanford_cars':
        num_classes=196
        train_transform = T.Compose([
            T.Resize(64),
            T.RandomCrop(64, padding=8),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )
        val_transform = T.Compose([
            T.Resize(64),
            T.CenterCrop(64),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )       
        data_root = os.path.join(data_root, 'StanfordCars')
        train_dst = datafree.datasets.StanfordCars(data_root, split='train', transform=train_transform)
        val_dst = datafree.datasets.StanfordCars(data_root, split='test', transform=val_transform)
    elif name=='tiny_imagenet':
        num_classes=200
        train_transform = T.Compose([
            T.RandomCrop(64, padding=4),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )
        val_transform = T.Compose([
            T.ToTensor(),
            T.Normalize( **NORMALIZE_DICT[name] )]
        )       
        data_root = os.path.join(data_root, 'tiny-imagenet-200')
        train_dst = datafree.datasets.TinyImageNet(data_root, split='train', transform=train_transform, download=True)
        val_dst = datafree.datasets.TinyImageNet(data_root, split='val', transform=val_transform, download=True)

    # For semantic segmentation
    elif name=='nyuv2':
        num_classes=13
        train_transform = sT.Compose([
            sT.Multi( sT.Resize(256), sT.Resize(256, interpolation=Image.NEAREST)),
            #sT.Multi( sT.ColorJitter(0.2, 0.2, 0.2), None),
            sT.Sync(  sT.RandomCrop(128),  sT.RandomCrop(128)),
            sT.Sync(  sT.RandomHorizontalFlip(), sT.RandomHorizontalFlip() ),
            sT.Multi( sT.ToTensor(), sT.ToTensor( normalize=False, dtype=torch.uint8) ),
            sT.Multi( sT.Normalize( **NORMALIZE_DICT[name] ), None) #, sT.Lambda(lambd=lambda x: (x.squeeze()-1).to(torch.long)) )
        ])
        val_transform = sT.Compose([
            sT.Multi( sT.Resize(256), sT.Resize(256, interpolation=Image.NEAREST)),
            sT.Multi( sT.ToTensor(),  sT.ToTensor( normalize=False, dtype=torch.uint8 ) ),
            sT.Multi( sT.Normalize( **NORMALIZE_DICT[name] ), None)#sT.Lambda(lambd=lambda x: (x.squeeze()-1).to(torch.long)) )
        ])
        data_root = os.path.join( data_root, 'NYUv2' )
        train_dst = datafree.datasets.NYUv2(data_root, split='train', transforms=train_transform)
        val_dst = datafree.datasets.NYUv2(data_root, split='test', transforms=val_transform)
    else:
        raise NotImplementedError
    if return_transform:
        return num_classes, train_dst, val_dst, train_transform, val_transform
    return num_classes, train_dst, val_dst
