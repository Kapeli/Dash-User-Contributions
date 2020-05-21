<?php

ini_set('memory_limit', -1);

use Sami\Sami;
use Sami\Version\GitVersionCollection;
use Sami\Version\SingleVersionCollection;
use Symfony\Component\Finder\Finder;

$iterator = Finder::create()
                  ->files()
                  ->name('*.php')
                  ->in($src = __DIR__ . '/carbon/src');

$versions = GitVersionCollection::create($src)
                                ->addFromTags('2.34.2');

return new Sami($iterator, [
    'build_dir' => __DIR__ . '/docset',
    'cache_dir' => "$src/../cache",
    'title' => 'Carbon',
    'versions' => $versions,
]);
