# ThirdParty Builder
Automatization tools to build third parties libraries for Lugdunum3D/Lugdunum and Lugdunum3D/LugBench

# Setup
```bash
pip install -r requirements.txt
```

# Build
You need to specify a yaml configuration file to build the libraries similar to this one:

```yml
shaderc:
    repository:
        tag: dcb30368cdbb91930aee6d86a0fc210f98304bcd

vulkan:
    repository:
        tag: 685295031d092db5417a5254e4f8b3e8024214cf

```

# Configuration files
Lugdunum3D/Lugdunum :
    thirdparty.yml

Lugdunum3D/LugBench :
    thirdparty.yml
    android_thirdparty.yml

# Android
- You msut set the env variable ANDROID_SDK_ROOT with the path to your Android SDK
- You need to specify --android=True as argument of build.py

# How to use
The python script `build.py` will use this configuration file to build an arborescence in the directory specified with the option `--path` (`thirdparty` by default).

```bash
python build.py config.yml
```

# How it works
The value for each `builder` is the configuration sent to it and is dependent of the `builder`, see each python file in the directory `builders/` to check the avalaible configuration for each one. The key `repository.tag` is mandatory, you can also specify the key `repository.uri` to specify which git repository you want to use.

