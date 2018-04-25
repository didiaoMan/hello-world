import utils
import tensorflow as tf
import tensorflow.contrib.distributions as tfd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys


# 查看生成图片效果
def show_imgs(images):
    images = (images + 1) / 2
    images = images.reshape((images.shape[0], 28, 28))
    for i in range(images.shape[0]):
        plt.subplot(1, images.shape[0], i + 1)
        plt.imshow(images[i], cmap='gray')
        plt.axis('off')

    plt.show()


batch_size = 64

# 载入数据
images, _ = utils.parse_data('data/mnist', 'train', True)
# 取出前128条数据,并将原来(0, 1)范围，变为(-1, 1),避免快速收敛仍然使用全部数据！！！
images = images * 2 - 1
# 限制特征在(-1, 1)区间中
images = np.clip(images, -1, 1)

# show_imgs(images[:10])
# sys.exit()
mean = tf.constant(np.zeros(shape=(100,)), dtype=tf.float32,
                   name='mean')
stddev = tf.constant(np.ones(shape=(100,)), dtype=tf.float32,
                     name='stddev')

# latent sample distribution
latent_sample_distribution = tfd.MultivariateNormalDiag(loc=mean,
                                                        scale_diag=stddev)
# 采样一个批次数据
samples = latent_sample_distribution.sample(
    sample_shape=[batch_size, ])

# latent sample placeholder
latent_sample = tf.placeholder(dtype=tf.float32,
                               shape=[None, 100],
                               name='latent_sample')

image = tf.placeholder(dtype=tf.float32,
                       shape=[None, 784],
                       name='images')

label = tf.placeholder(dtype=tf.float32,
                       shape=[None, 1],
                       name='label')

with tf.variable_scope('generator') as scope:
    gen_dense1 = tf.layers.dense(latent_sample, 128)
    gen_relu = tf.nn.leaky_relu(gen_dense1, alpha=0.01)
    gen_dense2 = tf.layers.dense(gen_relu, 784)
    generator = tf.nn.tanh(gen_dense2)


def discriminator(image):
    with tf.variable_scope('discriminator', reuse=tf.AUTO_REUSE) as scope:
        disc_dense1 = tf.layers.dense(image, 128, name='disc_dense1',
                                      reuse=tf.AUTO_REUSE)
        disc_relu = tf.nn.leaky_relu(disc_dense1, alpha=0.01)
        disc_dense2 = tf.layers.dense(disc_relu, 1, name='disc_dense2',
                                      reuse=tf.AUTO_REUSE)
        discriminator = tf.nn.sigmoid(disc_dense2)
    return (disc_dense1, disc_dense2, discriminator)


with tf.variable_scope('GAN', reuse=tf.AUTO_REUSE) as scope:
    disc_dense1, disc_dense2, only_disc = discriminator(image)
    _, _, gan = discriminator(generator)

# print(tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'generator'))

with tf.name_scope('loss_disc') as scope:
    loss_disc = label * tf.log(only_disc) + (1 - label) * tf.log(1 - only_disc)
    loss_disc = tf.reduce_mean(-loss_disc)

with tf.name_scope('loss_gen') as scope:
    loss_gen = label * tf.log(gan) + (1 - label) * tf.log(1 - gan)
    loss_gen = tf.reduce_mean(-loss_gen)

with tf.name_scope('opt_disc') as scope:
    opt_disc = tf.train.AdamOptimizer(0.001).minimize(loss_disc)

with tf.name_scope('opt_gen') as scope:
    opt_gen = tf.train.AdamOptimizer(0.0001).minimize(loss_gen,
                                                      var_list=tf.get_collection(
                                                          tf.GraphKeys.GLOBAL_VARIABLES,
                                                          'generator'))

# print(tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'GAN/discriminator'))
# sys.exit()

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    writer = tf.summary.FileWriter(logdir='log', graph=sess.graph)

    # 保存模型
    saver = tf.train.Saver()
    ckpt = tf.train.get_checkpoint_state(
        os.path.dirname('checkpoints/checkpoint'))
    if ckpt and ckpt.model_checkpoint_path:
        print('restore session ...')
        saver.restore(sess, ckpt.model_checkpoint_path)  # 恢复模型

    total_loss_disc = 0.0
    total_loss_gen = 0.0

    # 公共数据部分，一次分配即可
    labels_samples = np.zeros(shape=(batch_size, 1),
                              dtype=np.float32)
    labels_real = np.ones(shape=(batch_size, 1),
                          dtype=np.float32)
    # 没有使用smooth之前，很快数据溢出，nan
    labels_real_smooth = labels_real * (1 - 0.1)

    # 合并label
    finally_labels = np.concatenate((labels_samples, labels_real_smooth),
                                    axis=0)

    # 判断是否在graph中增加了新的节点
    sess.graph.finalize()
    for i in range(10000, 30000):
        # train discriminator

        # 训练一个批次的判别器
        # 采样生成一部分样本
        # !! 通过判断，这将在graph中加入新的节点造成，内存泄漏memory leak
        # !! 因此将这段代码放在外部
        # samples = latent_sample_distribution.sample(
        #     sample_shape=[batch_size, ])
        samples_array = sess.run(samples)
        # print(samples_array)
        # if i == 5001:
        #     break
        # continue
        images_samples = sess.run(generator, {latent_sample: samples_array})

        # 采样真实样本
        idx = np.random.choice(images.shape[0], batch_size)
        images_real = images[idx]
        # 合并两组数据
        finally_images = np.concatenate((images_samples, images_real),
                                        axis=0)

        opt, loss_value = sess.run([opt_disc, loss_disc],
                                   feed_dict={image: finally_images,
                                              label: finally_labels})
        # print(type(loss_value))
        total_loss_disc += loss_value
        # print(i, 'discriminator loss', loss_value)
        # if loss_value == float('nan'):  # python判断浮点数是否为nan
        if np.isnan(loss_value):  # numpy判断
            w = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,
                                  'GAN/discriminator/disc_dense1/kernel:0')
            print(w)
            dens1_w = sess.run(w)
            print('dens1_w', dens1_w)
            pred, disc_dense1_value, disc_dense2_value = sess.run(
                [only_disc, disc_dense1, disc_dense2],
                feed_dict={image: finally_images})
            print('finally_images', finally_images[:10])
            print('pred', pred[:10])
            print('disc_dense1_value', disc_dense1_value[:10])
            print('disc_dense2_value', disc_dense2_value[:10])
            sys.exit()
        if (i + 1) % 10 == 0:
            print(i, 'discriminator loss', total_loss_disc)
            total_loss_disc = 0.0

        # 训练generator一个批次
        # 注意这里使用labels_real为了使训练的generator更真实
        opt, loss_value = sess.run([opt_gen, loss_gen],
                                   feed_dict={latent_sample: samples_array,
                                              label: labels_real})

        total_loss_gen += loss_value
        # print(i, 'generator loss', loss_value)
        if (i + 1) % 10 == 0:
            print(i, 'generator loss', total_loss_gen)
            total_loss_gen = 0.0
            print('---------------------------------------')

        if (i + 1) % 500 == 0:
            saver.save(sess, 'checkpoints/simple_gan', i)

        if (i + 1) % 1000 == 0:
            # 采样一组查看效果
            # samples = latent_sample_distribution.sample(sample_shape=[10, ])
            samples_array = sess.run(samples)
            images_samples = sess.run(generator,
                                      {latent_sample: samples_array[:10]})
            show_imgs(images_samples)

writer.close()

# tensorflow运行越来越缓慢:https://www.zhihu.com/question/58577743
