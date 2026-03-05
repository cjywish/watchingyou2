import torch
import torch.nn as nn
import numpy as np

class HBMPINN(nn.Module):
    def __init__(self):
        super(HBMPINN, self).__init__()
        # 입력: x, y 좌표, 설정 온도(T_set), 설정 압력(P_set) -> 출력: 예측 온도(T)
        self.net = nn.Sequential(
            nn.Linear(4, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        
    def forward(self, x, y, t_set, p_set):
        inputs = torch.cat([x, y, t_set, p_set], dim=1)
        return self.net(inputs)

def physics_loss(model, x, y, t_set, p_set):
    """
    열전도 방정식 (Steady-state Heat Equation) 기반 Loss 계산
    Laplacian(T) = 0 (열원이 없는 정상 상태 가정)
    """
    x.requires_grad = True
    y.requires_grad = True
    
    t_pred = model(x, y, t_set, p_set)
    
    # 자동 미분(Automatic Differentiation)을 이용한 편미분 계산
    dt_dx = torch.autograd.grad(t_pred.sum(), x, create_graph=True)[0]
    dt_dy = torch.autograd.grad(t_pred.sum(), y, create_graph=True)[0]
    
    dt_dxx = torch.autograd.grad(dt_dx.sum(), x, create_graph=True)[0]
    dt_dyy = torch.autograd.grad(dt_dy.sum(), y, create_graph=True)[0]
    
    # 물리 법칙 오차: d^2T/dx^2 + d^2T/dy^2 = 0
    pde_loss = torch.mean((dt_dxx + dt_dyy)**2)
    return pde_loss