#!/bin/bash

DOCS_DIR=$(dirname $0)
cd $DOCS_DIR
DOTFILES=$(find . -name '*.dot')
for dotfile in $DOTFILES; do
  dot -Tpng -o ${dotfile%.*}.png ${dotfile}
done

~/src/cdk/asc pants_essentials_techtalk.asc
