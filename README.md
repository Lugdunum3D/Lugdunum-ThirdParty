# Lugdunum-ThirdParty
Automatization tools to build third parties libraries for Lugdunum3D/Lugdunum

# Setup

```bash
pip install -r requirements.txt
```

# Build

You need to specify a yml configuration file to build the libraries similar to this one:

```yml
shaderc:
    repository:
        tag: dcb30368cdbb91930aee6d86a0fc210f98304bcd

vulkan:
    repository:
        tag: 685295031d092db5417a5254e4f8b3e8024214cf

fmt:
    repository:
        tag: 07ed4215212324145bee94b94e34656923a4e9b4

googlemock:
    repository:
        tag: 294f72bc773c92410aa3c5ecdd6cd4a757c3fbf4

gltf2-loader:
    repository:
        tag: af5c74f82d2a563d4f659aebd91c27c8143edf9d
```

The value for each `builder` is the configuration send to it and is dependent of the `builder`, see each python file in the directory `builders/` to check the avalaible configuration for each one. The key `repository.tag` is mandatory, you can also specify the key `repository.uri` to specify which Git repository you want to use.

The python script `build.py` will use this configuration file to build an arborescence in the directory specified with the option `--path` (`thirdparty` by default).

```bash
python build.py config.yml
```
