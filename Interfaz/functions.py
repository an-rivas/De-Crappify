"""
https://github.com/fastai/fastai_dev/blob/master/dev_nb/104c_single_image_pred.ipynb Predict
"""
import fastai
import fastai.basics as fai #
import fastai.vision as fv #
import fastai.vision.gan as fgan #
from pathlib import Path #
import torch.nn as nn #
import torch
import matplotlib.pyplot as plt
import numpy as np
import torchvision.utils as utils
from torchvision import transforms
from os import remove
from PIL import Image, ImageDraw 

def _apply_img_changes(img, points):
    img1 = ImageDraw.Draw(img) 
    img1.line(points, fill ="white")
    
    return img

def redneuronal(file):
    fastai.device = torch.device('cpu')
    
    def load_data_crit(classes, img_size, bs, amount=1.):
        data = (fv.ImageList.from_folder(Path("../Images"),include=classes)
                .filter_by_rand(amount)
                .random_split_by_pct(0.1, seed=666)
                .label_from_folder(classes=classes)
                .transform(tfms, size=img_size)
                .databunch(bs=bs)
                .normalize(fv.imagenet_stats))
        data.c = 3
        return data

    def create_critic_learner(data, metrics):
        loss_gan = fgan.AdaptiveLoss(nn.BCEWithLogitsLoss())
        return fai.Learner(data, fgan.gan_critic(), metrics=metrics,
                           loss_func=loss_gan, wd=1e-2)

    def load_data_gen(img_size, batch_size, tfms, path_good, path_crappy, amount=1.):
        data = (fv.ImageImageList.from_folder(path_crappy)
                .filter_by_rand(amount)
                .random_split_by_pct(0.2)
                .label_from_func(lambda x: path_good/x.relative_to(path_crappy))
                .transform(tfms, size=img_size, tfm_y=True)
                .databunch(bs=batch_size)
                .normalize(fv.imagenet_stats, do_y=True))
        data.c = 3
        return data

    def l1_loss_flat(a,b):
        return F.l1_loss(a.squeeze(), b.squeeze())

    def create_learner_gen(data):
        return fv.unet_learner(data,fv.models.resnet34,blur=True,norm_type=fai.NormType.Weight,
                               self_attention=True,y_range=(-3.,3.),loss_func=l1_loss_flat,
                               metrics=[l1_loss_flat],wd=1e-2)

    tfms = fv.get_transforms(do_flip = False,max_zoom = 1.15,
                         max_lighting = 0.3,max_warp = 0.1,
                         p_affine = 0.5,p_lighting = 0.8)
                         
    path_good   = Path("../Images/StyleGAN") # neural network
    path_crappy = Path("../Images/crapifiadas") # neural network
    iteracion   = Path("02") #nuevo folder para la iteracion
    crappy_path = path_crappy/iteracion
    
    data_crit = load_data_crit(["generated", 'images1024x1024'],bs=4, img_size=256, amount=0.2)
    data_gen = load_data_gen(256, 2, tfms, path_good, crappy_path, 0.2)
    learn_crit = create_critic_learner(data_crit, metrics=None).load('../../models/02/3e-6_3critic-pretrain')
    learn_gen = create_learner_gen(data_gen).load('../../../../models/01/0.0005120000000000001-3')
    
    switcher = fai.partial(fgan.AdaptiveGANSwitcher,critic_thresh=0.65, gen_thresh=0.8)

    learn = fgan.GANLearner.from_learners(learn_gen,learn_crit,weights_gen=(1.,40.),
                                          show_img=True,switcher=switcher,
                                          opt_func=fai.partial(torch.optim.Adam,betas=(0.,0.99)),wd=1e-2)

    learn.callback_fns.append(fai.partial(fgan.GANDiscriminativeLR, mult_lr=5.))
    
    learn.load(f'../../../../models/03/3e-4_7juntos');
    img_size = (3, 256, 256)
    img = fv.open_image(file)
    img = img.resize(img_size)
    salida, _, _ = learn.predict(img)
    salida.save("salida.png")
    img = Image.open("salida.png")
    remove("salida.png")
    return img
    
