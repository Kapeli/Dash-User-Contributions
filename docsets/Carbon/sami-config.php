<?php

ini_set('memory_limit', -1);

// disable deprecation warnings in Sami
// (though these will need to be fixed eventually!)
error_reporting(E_ALL ^ E_DEPRECATED);

use Sami\Sami;
use Sami\Version\GitVersionCollection;
use Sami\Version\SingleVersionCollection;
use Symfony\Component\Finder\Finder;

$src = __DIR__ . '/carbon/src';
$version = getenv('VERSION_TAG');

$iterator = Finder::create()
                  ->files()
                  ->name('*.php')
                  ->in($src);

$versions = GitVersionCollection::create($src)
                                ->addFromTags($version);

return new Sami($iterator, [
    'build_dir' => __DIR__ . '/docs/api_docs',
    'cache_dir' => "$src/../cache",
    'title' => 'Carbon',
    'versions' => $versions,
]);
