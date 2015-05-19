## librlc

random linear code library

## dependence

1. gf\_complete

## build

1. build gf\_complete:

```
    cd gf_complete
    ./autogen.sh
    ./configure
    make
    cp src/.libs/libgf_complete.a PREFIX/librlc/gf_complete.a
```

2. build librlc

    `make`

## author

1. qing:<qing@hust.edu.cn>
2. lijian:<hustlijian@gmail.com>
3. ouyang:<373467963@qq.com>
