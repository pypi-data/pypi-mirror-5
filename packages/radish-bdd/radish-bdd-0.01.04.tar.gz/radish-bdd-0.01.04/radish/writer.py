# -*- coding: utf-8 -*-

import sys

from radish.colorful import colorful
from radish.config import Config
from radish.hookregistry import after, before
from radish.filesystemhelper import FileSystemHelper as fsh


@before.each_feature
def print_before_feature(feature):
    if not feature.is_dry_run():
        print(colorful.bold_white(feature.get_indentation() + "%*d. " % (len(str(Config().highest_feature_id)), feature.get_id()) + feature.get_sentence() + " " * (Config().longest_feature_text - len(feature.get_sentence()))) + " " * 10 + colorful.bold_black("# " + fsh.filename(feature.get_filename())))
        for l in feature.get_description().splitlines():
            colorful.out.white(feature.get_indentation() + " " * len(str(Config().highest_feature_id)) + "  " + l)
        print("")
        sys.stdout.flush()


@before.each_scenario
def print_before_scenario(scenario):
    if not scenario.is_dry_run():
        colorful.out.bold_white(scenario.get_indentation() + "%*d. %s" % (len(str(Config().highest_scenario_id)), scenario.get_id(), scenario.get_sentence()))
        sys.stdout.flush()


@after.each_scenario
def print_after_scenario(scenario):
    if not scenario.is_dry_run():
        print("")
        sys.stdout.flush()


@before.each_step
def print_before_step(step):
    if not step.is_dry_run():
        colorful.out.bold_brown(step.get_indentation() + "%*d. %s" % (len(str(Config().highest_step_id)), step.get_id(), step.get_sentence_splitted()[1]))
        sys.stdout.flush()


@after.each_step
def print_after_step(step):
    if not step.is_dry_run():
        splitted = step.get_sentence_splitted()
        if not Config().no_line_jump:
            sys.stdout.write("\033[A\033[K" * splitted[0])

        if step.has_passed() is None and Config().no_skipped_steps:
            return

        if step.has_passed():
            color_fn = colorful.out.bold_green
        elif step.has_passed() is False:
            color_fn = colorful.out.bold_red
        elif step.has_passed() is None:
            color_fn = colorful.out.cyan
        color_fn(step.get_indentation() + "%*d. %s" % (len(str(Config().highest_step_id)), step.get_id(), splitted[1]))

        if step.has_passed() is False:
            if Config().with_traceback:
                for l in step.get_fail_reason().get_traceback().splitlines():
                    colorful.out.red(step.get_sentence_indentation() + l)
            else:
                print(step.get_sentence_indentation() + colorful.red(step.get_fail_reason().get_name() + ": ") + colorful.bold_red(step.get_fail_reason().get_reason()))
        sys.stdout.flush()


@after.all
def print_after_all(endResult):
    if not Config().dry_run:
        white = colorful.bold_white
        green = colorful.bold_green
        red = colorful.bold_red
        cyan = colorful.cyan

        feature_text = green(str(endResult.get_passed_features()) + " passed")
        if endResult.get_failed_features() > 0:
            feature_text += white(", ") + red(str(endResult.get_failed_features()) + " failed")

        scenario_text = green(str(endResult.get_passed_scenarios()) + " passed")
        if endResult.get_failed_scenarios() > 0:
            scenario_text += white(", ") + red(str(endResult.get_failed_scenarios()) + " failed")

        step_text = green(str(endResult.get_passed_steps()) + " passed")
        if endResult.get_failed_steps() > 0:
            step_text += white(", ") + red(str(endResult.get_failed_steps()) + " failed")
        if endResult.get_skipped_steps() > 0:
            step_text += white(", ") + cyan(str(endResult.get_skipped_steps()) + " skipped")

        colorful.out.bold_white(str(endResult.get_total_features()) + " features (%s" % (feature_text) + white(")"))
        colorful.out.bold_white(str(endResult.get_total_scenarios()) + " scenarios (%s" % (scenario_text) + white(")"))
        colorful.out.bold_white(str(endResult.get_total_steps()) + " steps (%s" % (step_text) + white(")"))

        if not Config().no_duration:
            duration = 0.0
            for f in endResult.get_features():
                duration += f.get_duration()
            colorful.out.cyan("(finished within %d minutes and %.2f seconds)" % (duration / 60, float(duration) % 60.0))
        sys.stdout.flush()
