import torchvision.transforms as standard_transforms
from torch.utils.data import DataLoader

import misc.transforms as own_transforms
from datasets.Multiple.loader import DynamicDataset, CollateFN
from datasets.Multiple.settings import cfg_data


def loading_data():
    mean_std = cfg_data.MEAN_STD
    log_para = cfg_data.LOG_PARA

    cl = CollateFN(cfg_data.TRAIN_SIZE)
    collate = cl.collate if cfg_data.COLLATE_FN and cfg_data.TRAIN_BATCH_SIZE != 1 else None

    # Add here specific transform func : 
    # Choose differents combinaison of transformations for each dataset
    train_main_transform_SHHA = own_transforms.Compose([
        own_transforms.RandomCrop(cfg_data.TRAIN_SIZE),
        own_transforms.ColorJitter(brightness=0.5, contrast=0.5),
        own_transforms.RandomHorizontallyFlip(),
    ])

    train_main_transform_SHHB = own_transforms.Compose([
        own_transforms.RandomCrop(cfg_data.TRAIN_SIZE),
        own_transforms.ColorJitter(brightness=0.5, contrast=0.5),
        own_transforms.RandomDownOverSampling(4),
        own_transforms.RandomHorizontallyFlip(),
    ])

    train_main_transform_WE = own_transforms.Compose([
        own_transforms.RandomCrop(cfg_data.TRAIN_SIZE),
        own_transforms.ColorJitter(brightness=0.5, contrast=0.5),
        own_transforms.RandomHorizontallyFlip(),
    ])

    train_main_transform_BG = own_transforms.Compose([
        own_transforms.RandomCrop(cfg_data.TRAIN_SIZE),
        own_transforms.ColorJitter(brightness=0.5, contrast=0.5),
        own_transforms.RandomHorizontallyFlip(),
        own_transforms.WriteTexts(factor=0.75),
    ])

    train_main_transform_JHU = own_transforms.Compose([
        own_transforms.RandomCrop(cfg_data.TRAIN_SIZE),
        own_transforms.ColorJitter(brightness=0.5, contrast=0.5),
        own_transforms.RandomHorizontallyFlip(),
    ])

    train_main_transform_GCC = own_transforms.Compose([
        own_transforms.RandomCrop(cfg_data.TRAIN_SIZE),
        own_transforms.RandomHorizontallyFlip()
    ])

    specific_transform = {"SHHA__transform": train_main_transform_SHHA,
                          "SHHB__transform": train_main_transform_SHHB,
                          "GCC__transform": train_main_transform_GCC,
                          "WE__transform": train_main_transform_WE,
                          "BG__transform": train_main_transform_BG,
                          "JHU__transform": train_main_transform_JHU,
                          }

    if specific_transform:
        cfg_data.PATH_SETTINGS.update(specific_transform)

    # global transform
    train_main_transform = own_transforms.Compose([
        own_transforms.RandomHorizontallyFlip()
    ])

    img_transform = standard_transforms.Compose([
        standard_transforms.ToTensor(),
        standard_transforms.Normalize(*mean_std)
    ])

    gt_transform = standard_transforms.Compose([
        own_transforms.LabelNormalize(log_para)
    ])

    restore_transform = standard_transforms.Compose([
        own_transforms.DeNormalize(*mean_std),
        standard_transforms.ToPILImage()
    ])

    train_set = DynamicDataset(couple_datasets=cfg_data.LIST_C_DATASETS,
                               mode='train',
                               main_transform=train_main_transform,
                               img_transform=img_transform,
                               gt_transform=gt_transform,
                               image_size=cfg_data.IMAGE_SIZE,
                               **cfg_data.PATH_SETTINGS)

    train_loader = DataLoader(train_set,
                              batch_size=cfg_data.TRAIN_BATCH_SIZE,
                              num_workers=8,
                              collate_fn=collate,
                              shuffle=True,
                              drop_last=True)

    val_set = DynamicDataset(couple_datasets=cfg_data.LIST_C_DATASETS,
                             mode='test',
                             main_transform=None,
                             img_transform=img_transform,
                             gt_transform=gt_transform,
                             image_size=cfg_data.IMAGE_SIZE,
                             **cfg_data.PATH_SETTINGS)
    val_loader = None
    if len(val_set) > 0:
        val_loader = DataLoader(val_set,
                                batch_size=cfg_data.VAL_BATCH_SIZE,
                                num_workers=8,
                                shuffle=True,
                                drop_last=False)

    return train_loader, val_loader, restore_transform
