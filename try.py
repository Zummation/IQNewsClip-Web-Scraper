from multiprocessing import Process


def func(name):
    for i in range(5):
        print(name, i)

if __name__ == '__main__':
    name = ['a', 'b']
    procs = []
    for i in range(2):
        proc = Process(target=func, args=(name[i],))
        procs += [proc]
        proc.start()



