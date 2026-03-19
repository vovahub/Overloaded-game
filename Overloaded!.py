import pyglet
import pymunk
import math
import os
from PIL import ImageFont
from threading import Thread
import time

所在目录 = os.path.dirname(__file__)
window = pyglet.window.Window(1280, 720, "Overloaded!", resizable=True) # 设置窗口, vsync=True
window.set_minimum_size(640, 360) # 设置窗口最小宽高
window.set_maximum_size(1920, 1080) # 设置窗口最大宽高
按键 = pyglet.window.key.KeyStateHandler()
window.push_handlers(按键)

def 过渡(目前值, 目标值, 过渡参数, adt):
    结果 = 目前值 + ( (目标值 - 目前值) / 过渡参数) * adt * 60
    return 结果
def 角度(主观X,主观Y,被主观X,被主观Y):
    return - math.atan2(被主观Y - 主观Y, 被主观X - 主观X) * 180 / math.pi
def 长度(AX,AY,BX,BY):
    return math.hypot(BX-AX, BY-AY)

状态_玩家血量 = 100
状态_玩家能量 = 150
cam_X, cam_Y = (0,0)
cam_鼠标X = 0
cam_鼠标Y = 0
cam_过渡系数 = 10
cam_鼠标偏移系数 = 0.5

物体 = {}
物体size = {}
def 空间创建(重力x=0,重力y=-500,阻尼=0.5,迭代=10,启动空间哈希加速=False,空间哈希加速网格大小=100):
    global 物理空间
    物理空间 = pymunk.Space() # 创建
    物理空间.gravity = (重力x, 重力y) # 空间向量_其实就是重力方向
    物理空间.damping = 阻尼 # 阻尼,越小空气越粘稠
    物理空间.iterations = 迭代 # 碰撞迭代,次数越多或许越精准但是可能更卡
    if 启动空间哈希加速:
        物理空间.use_spatial_hash(cell_size=空间哈希加速网格大小) #空间哈希加速
def 模拟(DT):
    物理空间.step(DT)
def 创建矩形物体(名字,中心坐标X,中心坐标Y,矩形X,矩形Y,角度,摩擦力=0.1,弹性=0.0,静态=False,物体质量=0.1,转动惯量=float('inf')):
    global 物体,物体size
    物体[名字] = {}
    if 静态:
        物体[名字]["body"] = pymunk.Body(body_type=pymunk.Body.STATIC) # 设置类型_静态
    else:
        物体[名字]["body"] = pymunk.Body(mass=物体质量, moment=转动惯量) # 设置类型_动态
    物体[名字]["body"].position = (中心坐标X, 中心坐标Y) # 设置初始位置
    物体[名字]["body"].angle = 角度 * math.pi / 180
    物体[名字]["shape"] = pymunk.Poly.create_box(物体[名字]["body"], (矩形X, 矩形Y)) # 创建矩形碰撞箱
    物体size[名字] = (矩形X, 矩形Y)
    物体[名字]["shape"].friction = 摩擦力
    物体[名字]["shape"].elasticity = 弹性
    物理空间.add(物体[名字]["body"],物体[名字]["shape"])

空间创建(重力y=-1000,阻尼=0.7)
创建矩形物体("玩家",window.width//2,window.height//2,50,50,0,0.3,0.5,False,0.1)
创建矩形物体("地板",window.width//2,25,2000,25,25,0.3,0.5,True,0.1)
创建矩形物体("地板2",window.width//2,25,200,25,0,0.3,0.5,True,0.1)

batch_物体 = pyglet.graphics.Batch()
渲染_物体 = {}
# ------------------------------------渲染函数初始化------------------------------------
# 物体_基础
batch_物体 = pyglet.graphics.Batch()
渲染_物体 = {}
# 物理_对象
for 该物体 in list(物体.keys()):
    该物体坐标X, 该物体坐标Y = 物体[该物体]["body"].position
    该物体D = 物体[该物体]["body"].angle * 180 / math.pi
    渲染_物体[该物体] = pyglet.shapes.Rectangle(
        x = 该物体坐标X-cam_X,
        y = 该物体坐标Y-cam_Y,
        width = 物体size[该物体][0],
        height = 物体size[该物体][1],
        color = (255, 255, 255),
        batch = batch_物体
    )
    渲染_物体[该物体].anchor_position = (物体size[该物体][0]/2, 物体size[该物体][1]/2)
    渲染_物体[该物体].rotation = - 该物体D
# --------------------
# 状态_基础
batch_玩家状态 = pyglet.graphics.Batch()
渲染_玩家状态 = {}
过渡_状态_玩家血量 = 0
过渡_状态_玩家能量 = 0
# 状态_对象
渲染_玩家状态["血量_背景"] = pyglet.shapes.Rectangle(
    x = window.width-25-1,
    y = 5-1,
    width = 20+2,
    height = 2 * 100 +2,
    color = (255, 255, 255, 150),
    batch = batch_玩家状态
)
渲染_玩家状态["血量_过度条"] = pyglet.shapes.Rectangle(
    x = window.width-25,
    y = 5,
    width = 20,
    height = 2 * max(0,min(过渡_状态_玩家血量,100)),
    color = (207, 255, 17, 200),
    batch = batch_玩家状态
)
渲染_玩家状态["血量_前景"] = pyglet.shapes.Rectangle(
    x = window.width-25,
    y = 5,
    width = 20,
    height = 2 * max(0,min(状态_玩家血量,100)),
    color = (255, 0, 0, 200),
    batch = batch_玩家状态
)
渲染_玩家状态["能量_背景"] = pyglet.shapes.Rectangle(
    x = 5 - 1,
    y = 5 - 1,
    width = 4 * 150 + 2,
    height = 20 + 2,
    color = (255, 255, 255, 150),
    batch = batch_玩家状态
)
渲染_玩家状态["能量_过渡条"] = pyglet.shapes.Rectangle(
    x = 5,
    y = 5,
    width = 4 * max(0,min(过渡_状态_玩家能量,150)),
    height = 20,
    color = (34, 122, 255, 200),
    batch = batch_玩家状态
)
渲染_玩家状态["能量_前景"] = pyglet.shapes.Rectangle(
    x = 5,
    y = 5,
    width = 4 * max(0,min(状态_玩家能量,150)),
    height = 20,
    color = (48, 0, 238, 200),
    batch = batch_玩家状态
)
# 渲染_玩家状态["能量_前景2"] = pyglet.shapes.Rectangle(
#     x = 5,
#     y = 5,
#     width = 4 * max(0,min(状态_玩家能量,150)),
#     height = 20,
#     color = (48, 0, 238, 200),
#     batch = batch_玩家状态
# )
# 渲染_玩家状态["能量_前景3"] = pyglet.shapes.Rectangle(
#     x = 5,
#     y = 5,
#     width = 4 * max(0,min(状态_玩家能量,150)),
#     height = 20,
#     color = (48, 0, 238, 200),
#     batch = batch_玩家状态
# )
# --------------------
# 指示红线_基础
batch_指示红线 = pyglet.graphics.Batch()
渲染_指示红线 = {}
过渡_指示红线_主体线_x = 0
过渡_指示红线_主体线_y = 0
玩家坐标X, 玩家坐标Y = 物体["玩家"]["body"].position
# 指示红线_对象
渲染_指示红线["主体线"] = pyglet.shapes.Rectangle(
    x = 玩家坐标X - cam_X,
    y = 玩家坐标Y - cam_Y,
    width = 长度(玩家坐标X,玩家坐标Y,cam_鼠标X,cam_鼠标Y),
    height = 1,
    color = (255, 0, 0, 200),
    batch = batch_指示红线
)
渲染_指示红线["主体线"].rotation = 角度(玩家坐标X,玩家坐标Y,cam_鼠标X,cam_鼠标Y)
# ------------------------------------渲染更新函数------------------------------------
def 渲染任务_指示红线():
    # global 过渡_指示红线_主体线_x,过渡_指示红线_主体线_y
    # 指示红线过渡参数 = 1.5
    # 玩家坐标X, 玩家坐标Y = 物体["玩家"]["body"].position
    # # 用过渡解决参数计算延迟鬼畜问题
    # 过渡_指示红线_主体线_x = 过渡(过渡_指示红线_主体线_x,玩家坐标X - cam_X,指示红线过渡参数,dt)
    # 过渡_指示红线_主体线_y = 过渡(过渡_指示红线_主体线_y,玩家坐标Y - cam_Y,指示红线过渡参数,dt)
    # 渲染_指示红线["主体线"].x = 过渡_指示红线_主体线_x
    # 渲染_指示红线["主体线"].y = 过渡_指示红线_主体线_y
    # 渲染_指示红线["主体线"].width = 长度(玩家坐标X,玩家坐标Y,cam_鼠标X,cam_鼠标Y)
    # 渲染_指示红线["主体线"].rotation = 角度(玩家坐标X,玩家坐标Y,cam_鼠标X,cam_鼠标Y)
    global 过渡_指示红线_主体线_x,过渡_指示红线_主体线_y
    玩家坐标X, 玩家坐标Y = 物体["玩家"]["body"].position
    渲染_指示红线["主体线"].x = 玩家坐标X - cam_X
    渲染_指示红线["主体线"].y = 玩家坐标Y - cam_Y
    渲染_指示红线["主体线"].width = 长度(玩家坐标X,玩家坐标Y,cam_鼠标X,cam_鼠标Y)
    渲染_指示红线["主体线"].rotation = 角度(玩家坐标X,玩家坐标Y,cam_鼠标X,cam_鼠标Y)
def 渲染任务_物理体(dt):
    模拟(dt)
    for 该物体 in list(渲染_物体.keys()):
        该物体坐标X, 该物体坐标Y = 物体[该物体]["body"].position
        该物体D = 物体[该物体]["body"].angle * 180 / math.pi
        渲染_物体[该物体].x = 该物体坐标X-cam_X
        渲染_物体[该物体].y = 该物体坐标Y-cam_Y
        渲染_物体[该物体].rotation = - 该物体D
    # 红线渲染与物理体渲染放在一起,这是为了防止出现抖动,即使牺牲了规整
    渲染任务_指示红线()
def 渲染任务_玩家状态(dt):
    global 过渡_状态_玩家血量,过渡_状态_玩家能量
    过渡参数_过渡条 = 10
    渲染_玩家状态["血量_背景"].x = window.width-25-1
    渲染_玩家状态["血量_背景"].height = 2 * 100 +2
    渲染_玩家状态["血量_过度条"].x = window.width-25
    渲染_玩家状态["血量_过度条"].height = 2 * max(0,min(过渡_状态_玩家血量,100))
    渲染_玩家状态["血量_前景"].x = window.width-25
    渲染_玩家状态["血量_前景"].height = 2 * max(0,min(状态_玩家血量,100))
    渲染_玩家状态["能量_背景"].width = 4 * 150 + 2
    渲染_玩家状态["能量_过渡条"].width = 4 * max(0,min(过渡_状态_玩家能量,150))
    渲染_玩家状态["能量_前景"].width = 4 * max(0,min(状态_玩家能量,150))
    过渡_状态_玩家血量 = 过渡(过渡_状态_玩家血量,状态_玩家血量,过渡参数_过渡条,dt)
    过渡_状态_玩家能量 = 过渡(过渡_状态_玩家能量,状态_玩家能量,过渡参数_过渡条,dt)

    
@window.event
def on_draw():
    window.clear()
    batch_物体.draw()
    batch_玩家状态.draw()
    batch_指示红线.draw()
    # pyglet.clock.tick()
        
@window.event
def on_activate():# 窗口为焦点
    pass

@window.event  
def on_deactivate(): # 窗口不为焦点(not)
    pass

def 物理引擎模拟(dt):
    模拟(dt)
速度 = 150
移动跨越补偿 = 100
跳跃力度 = 8000
冲刺力度倍数 = 50
def 玩家移动_平移(dt):
    玩家碰到的东西 = 物理空间.shape_query(物体["玩家"]["shape"])
    if 按键[pyglet.window.key.W]:
        pass
    if 按键[pyglet.window.key.S]:
        pass
    if 按键[pyglet.window.key.A]:
        物体["玩家"]["body"].apply_force_at_local_point((-速度, 0))
        if 玩家碰到的东西:
            物体["玩家"]["body"].apply_force_at_local_point((0, 移动跨越补偿)) # 为了解决斜坡上不去的问题,简单粗暴
    if 按键[pyglet.window.key.D]:
        物体["玩家"]["body"].apply_force_at_local_point((速度, 0))
        if 玩家碰到的东西:
            物体["玩家"]["body"].apply_force_at_local_point((0, 移动跨越补偿)) # 为了解决斜坡上不去的问题,简单粗暴
可以跳跃 = True
def 玩家移动_跳跃(dt):
    global 可以跳跃
    if 按键[pyglet.window.key.SPACE]:
        if 按键[pyglet.window.key.SPACE] and 可以跳跃:
            物体["玩家"]["body"].apply_force_at_local_point((0, 跳跃力度))
        可以跳跃 = False
    if not 按键[pyglet.window.key.SPACE]:
        可以跳跃 = True
可以冲刺 = True
def 玩家移动_冲刺(dt):
    global 可以冲刺,冲刺力度倍数
    if 按键[pyglet.window.key.F]:
        if 按键[pyglet.window.key.F] and 可以冲刺:
            玩家X, 玩家Y = 物体["玩家"]["body"].position
            方向X = cam_鼠标X - 玩家X
            方向Y = 玩家Y - cam_鼠标Y
            力_X = 方向X * 冲刺力度倍数
            力_Y = -方向Y * 冲刺力度倍数
            物体["玩家"]["body"].apply_force_at_local_point((力_X, 力_Y))
        可以冲刺 = False
    if not 按键[pyglet.window.key.F]:
        可以冲刺 = True
# 你好呀!心情不好?data/assets/music有一个Subwoofer Lullaby - C418你可以放松下
def 状态恢复(dt):
    global 状态_玩家血量,状态_玩家能量
    if not 状态_玩家血量 >= 100:
        状态_玩家血量 += 0.1
    if not 状态_玩家能量 >= 150:
        状态_玩家能量 += 0.1
def 摄像机系统(dt):
    global cam_X,cam_Y,cam_鼠标偏移系数,cam_过渡系数,cam_鼠标X,cam_鼠标Y,鼠标x,鼠标y
    cam_X_基础 = 物体["玩家"]["body"].position[0] - window.width//2
    cam_Y_基础 = 物体["玩家"]["body"].position[1] - window.height//2
    鼠标x, 鼠标y = window._mouse_x, window._mouse_y
    偏移x = 鼠标x - window.width//2
    偏移y = 鼠标y - window.height//2
    cam_X_目标 = cam_X_基础 + 偏移x * cam_鼠标偏移系数
    cam_Y_目标 = cam_Y_基础 + 偏移y * cam_鼠标偏移系数
    cam_X = 过渡(cam_X,cam_X_目标,cam_过渡系数,dt)
    cam_Y = 过渡(cam_Y,cam_Y_目标,cam_过渡系数,dt)
    cam_鼠标X = 鼠标x + cam_X
    cam_鼠标Y = 鼠标y + cam_Y
pyglet.clock.schedule_interval(玩家移动_平移, 1/90.0)
pyglet.clock.schedule_interval(玩家移动_跳跃, 1/60.0)
pyglet.clock.schedule_interval(玩家移动_冲刺, 1/60.0)
pyglet.clock.schedule_interval(摄像机系统, 1/60.0)
pyglet.clock.schedule_interval(渲染任务_物理体, 1/120.0)
pyglet.clock.schedule_interval(渲染任务_玩家状态, 1/120.0)
# pyglet.clock.schedule_interval(渲染任务_指示红线, 1/120.0)
pyglet.clock.schedule_interval(状态恢复, 1/30.0)
pyglet.app.run()
"""SW4gbXkgZXllcywgbWFraW5nIGEgZ2FtZSB3aXRoIGNvZGUgcmF0aGVyIHRoYW4gYW4gZW
5naW5lIG1pZ2h0IGJlIG11Y2ggaGFyZGVyIHRoYW4gd3JpdGluZyBhIHNlcnZlciBsb2dpYyw
gYnV0IEkgdGFrZSBpdCBhcyBhIHdheSB0byBsZWFybiBweWdsZXQsIG5vdCBhcyBhIHRhc2su
IFBlcmhhcHMgbXkgdmFsdWVzIGFyZSBjb21tZW5kYWJsZSwgYnV0IEkgdGhpbmsgSSBtaWdod
CBzdG9wIHdvcmtpbmcgb24gdGhpcyBhdCBhbnkgdGltZSBpbiBhIGRheS4gSW4gc2hvcnQsIE
kgaG9wZSB0aGF0IHdoZW4gSSBzZWUgdGhpcyBzZW50ZW5jZSBpbiB0aGUgZnV0dXJlLCBJIHd
pbGwgY29udGludWUgdG8gd29yayBvbiBpdCBhbmQgbm90IGxldCBteSBwcmVzZW50IHNlbGYg
cmVncmV0IGl0Lg=="""