ECharts Dash Docset
=======================

This is the Dash Docset for [ECharts](http://echarts.baidu.com), maintained by [Ovilia](https://github.com/Ovilia), team member of ECharts.

## Generate the Docset

1. Clone [github.com/ecomfe/echarts-doc](https://github.com/ecomfe/echarts-doc) project.

2. `cd public/documents/dash`

3. `node ../dashing.js`

4. Build
  - To build Docset in English: `./dashing build echarts -f dashing-en.json -s ./en`  
  - To build Docset in Chinese: `./dashing build echarts -f dashing-cn.json -s ./cn`

5. The generated Docset is under current directory. Change version number in `echarts.docset/Contents/Info.plist` if you may.
