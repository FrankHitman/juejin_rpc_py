#coding=utf-8
import threading
# from concurrent import futures


# 通过condition完成协同读诗

class XiaoAi(threading.Thread):
    def __init__(self, cond):
        super(XiaoAi, self).__init__(name="小爱")
        self.cond = cond

    def run(self):
        with self.cond:
            self.cond.wait()
            print("{} : 在 ".format(self.name))
            self.cond.notify()

            self.cond.wait()
            print("{} : 好啊 ".format(self.name))
            self.cond.notify()

            self.cond.wait()
            print("{} : 君住长江尾 ".format(self.name))
            self.cond.notify()

            self.cond.wait()
            print("{} : 共饮长江水 ".format(self.name))
            self.cond.notify()

            self.cond.wait()
            print("{} : 此恨何时已 ".format(self.name))
            self.cond.notify()

            self.cond.wait()
            print("{} : 定不负相思意 ".format(self.name))
            self.cond.notify()


class TianMao(threading.Thread):
    def __init__(self, cond):
        super(TianMao, self).__init__(name="天猫精灵")
        self.cond = cond

    def run(self):
        with self.cond:
            print("{} : 小爱同学 ".format(self.name))
            self.cond.notify()
            self.cond.wait()

            print("{} : 我们来对古诗吧 ".format(self.name))
            self.cond.notify()
            self.cond.wait()

            print("{} : 我住长江头 ".format(self.name))
            self.cond.notify()
            self.cond.wait()

            print("{} : 日日思君不见君 ".format(self.name))
            self.cond.notify()
            self.cond.wait()

            print("{} : 此水几时休 ".format(self.name))
            self.cond.notify()
            self.cond.wait()

            print("{} : 只愿君心似我心 ".format(self.name))
            self.cond.notify()
            self.cond.wait()


if __name__ == "__main__":
    cond = threading.Condition()
    xiaoai = XiaoAi(cond)
    tianmao = TianMao(cond)

    # 启动顺序很重要
    # 在调用with cond之后才能调用wait或者notify方法
    # condition有两层锁， 一把底层锁会在线程调用了wait方法的时候释放， 上面的锁会在每次调用wait的时候分配一把并放入到cond的等待队列中，等到notify方法的唤醒
    xiaoai.start()
    tianmao.start()

# output
# 天猫精灵 : 小爱同学
# 小爱 : 在
# 天猫精灵 : 我们来对古诗吧
# 小爱 : 好啊
# 天猫精灵 : 我住长江头
# 小爱 : 君住长江尾
# 天猫精灵 : 日日思君不见君
# 小爱 : 共饮长江水
# 天猫精灵 : 此水几时休
# 小爱 : 此恨何时已
# 天猫精灵 : 只愿君心似我心
# 小爱 : 定不负相思意