# Makefile for source rpm: audit
# $Id$
NAME := audit
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
