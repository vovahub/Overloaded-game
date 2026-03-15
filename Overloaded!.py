import pyglet
import pymunk
import math

window = pyglet.window.Window(1280, 720, "My App", resizable=True) # 设置窗口
window.set_minimum_size(640, 360) # 设置窗口最小宽高
window.set_maximum_size(1920, 1080) # 设置窗口最大宽高
按键 = pyglet.window.key.KeyStateHandler()
window.push_handlers(按键)

物体 = {}
物体size = {}
def 空间创建(重力x=0,重力y=-500,阻尼=1,迭代=10,启动空间哈希加速=False,空间哈希加速网格大小=100):
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

空间创建()
创建矩形物体("玩家",window.width//2,window.height//2,50,50,0,0.5,0,False,0.1)
创建矩形物体("地板",window.width//2,25,200,25,0,0.1,0,True,0.1)
玩家数据 = {
    "x":window.width//2,
    "y":window.height//2,
    "d":90
}
@window.event
def on_draw():
    window.clear()
    for 该物体 in list(物体.keys()):
        该物体坐标X, 该物体坐标Y = 物体[该物体]["body"].position
        该物体D = 物体[该物体]["body"].angle * 180 / math.pi
        渲染 = pyglet.shapes.Rectangle(
            x=该物体坐标X,
            y=该物体坐标Y,
            width=物体size[该物体][0],
            height=物体size[该物体][1],
            color=(255, 255, 255)
        )
        渲染.anchor_position = (物体size[该物体][0]/2, 物体size[该物体][1]/2)
        渲染.rotation = - 该物体D
        渲染.draw()
        
@window.event
def on_activate():# 窗口为焦点
    pass

@window.event  
def on_deactivate(): # 窗口不为焦点(not)
    pass

def 物理引擎模拟(dt):
    模拟(dt)
速度 = 50
跳跃力度 = 2000
def 玩家移动_平移(dt):
    global 玩家数据
    玩家数据["x"], 玩家数据["y"] = 物体["玩家"]["body"].position
    玩家数据["d"] = 物体["玩家"]["body"].angle * 180 / math.pi
    if 按键[pyglet.window.key.W]:
        pass
    if 按键[pyglet.window.key.S]:
        pass
    if 按键[pyglet.window.key.A]:
        物体["玩家"]["body"].apply_force_at_local_point((-速度, 0))
    if 按键[pyglet.window.key.D]:
        物体["玩家"]["body"].apply_force_at_local_point((速度, 0))
可以跳跃 = True
def 玩家移动_跳跃(dt):
    global 可以跳跃
    if 按键[pyglet.window.key.SPACE]:
        if 按键[pyglet.window.key.SPACE] and 可以跳跃:
            物体["玩家"]["body"].apply_force_at_local_point((0, 跳跃力度))
        可以跳跃 = False  # 进入冷却
    # 检测空格松开
    if not 按键[pyglet.window.key.SPACE]:
        可以跳跃 = True  # 重置跳跃状态

pyglet.clock.schedule_interval(玩家移动_平移, 1/90.0)
pyglet.clock.schedule_interval(玩家移动_跳跃, 1/90.0)
pyglet.clock.schedule_interval(物理引擎模拟, 1/120.0)
pyglet.app.run()