const fs = require('fs')
const rp = require('request')
const path = require('path')
const walk = require('fs-walk').files
const async = require('async')
const mkdirp = require('mkdirp')
const request = require('request')

const docset = path.join(path.resolve(process.argv[2]), 'Contents/Resources/Documents')

// "https://github.com/ReactiveX/RxJava/wiki/images/rx-operators/publishConnect.png"
// "https://raw.github.com/wiki/ReactiveX/RxJava/images/rx-operators/amb.png"
const REG_SRC = /"([^"]+github\.com\/[^"]+\/(images\/[^"]+\.png))"/g

if (!fs.existsSync(docset)) {
  console.error(`${process.argv[2]} not a valid javadoc docset`)
  return process.exit(1)
}

async.waterfall([
  function (done) {
    console.log('1. Walking through HTMLs and replacing urls...')
    var files = {}
    walk(docset, function (basedir, filename, stat, next) {
      if (path.extname(filename) != '.html') {
        return next()
      }

      var file = path.join(basedir, filename)

      console.log(path.relative(docset, file))

      var content = fs.readFileSync(file, 'utf-8')

      content = content.replace(REG_SRC, function (match, url, local) {
        local = path.resolve(docset, local)
        var relative = path.relative(basedir, local)
        if (!files[local]) {
          console.log(`  ${relative}: \t${url}`)
        }
        files[local] = url
        return relative
      })

      fs.writeFileSync(file, content)

      next()
    }, function (err) {
      console.log('')
      done(err, files)
    })
  },
  function (files, done) {
    console.log('2. Preparing dirs...')
    async.forEachOf(files, function (url, local, next) {
      mkdirp(path.dirname(local), next)
    }, function (err) {
      console.log('')
      done(err, files)
    })
  },
  function (files, done) {
    console.log('3. Downloading images...')
    async.forEachOfLimit(files, 5, function (url, local, next) {
      console.log(`  ${url}`)
      request(url, next).pipe(fs.createWriteStream(local))
    }, function (err) {
      console.log('')
      done(err)
    })
  }
], function (err) {
  if (err) {
    console.error(err.stack)
    return process.exit(3)
  } else {
    console.log('done')
  }
})
