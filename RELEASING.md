# Publishing New Versions

Please follow the steps below when releasing a new version. This helps ensure
that the experience for users is consistent and well documented.

Publishing releases occurs in two parts: tagging in the Git repository and
publishing on Github; and publishing to pypi.

## Versioning

The `timber-python` package uses [Semantic Versioning](http://semver.org/) for its
releases. This means you should think critically about how the changes made in
the library impact functionality. The Semantic Versioning summary has a good
overview. When in doubt, prefer incrementing the MINOR version over the PATCH
version.

To check what changes have been made since the last release, you can use the
`git log` function. Let's say the last release was `2.0.1`; the tag for that
is `v2.0.1`, so we can see the changes between that release and the `HEAD` of
`master` using the following command:

```bash
git log --pretty=oneline v1.0.7..master
```

You can drop the `--pretty=oneline` to view the full commit messages, but the
general size of the comparison should give you a good idea of how much change
has occured.

## Git Tagging

Git tags are powerful tools that can be used to reference specific commits in
the repository. In addition to helping us manage which commits are included in a
release, they are also used by the documentation system to build reference links
back to the original source code.

`timber-python` releases should _always_ use annotated Git tags. The tag should
be of the form `v#{Version}`. So, if you're publishing version 5.0.9, the tag is
`v5.0.9`. If you are publishing version 1.0.7-rc.1, the tag is `v1.0.7-rc.1`.
Naming the tag improperly will result in the links from the documentation to the
source code breaking.

Annotated tags can be created using `git tag -a`. For example, to create tag
`v1.7.1` at the current commit, you would use the following command:

```bash
git tag -a v1.7.1
```

This opens the default editor from your shell profile where you are expected to
provide the tag's message. When you save and quit the editor, the tag will be
created. If you exit the editor before saving, the tag creation will be aborted.

The tag message should take the following form:

```
#{Version} - #{dd MMMM YYYY}

#{Changes}
```

The changes should be a list summarizing the changes that were made, possibly
with links to the relevant issues and pull requests. You may also have a longer
prose description at the top. The date should be the current date. The format is
Here's a full example:

```
2.9.0-rc.3 - 07 June 2017

This is a release candidate for the new syslog logger backend fixing a number of
reported issues.

  - The socket will now be released cleanly even if the backend encounters an
    error (see #1058, #1067, and #1069)
  - The output will now be truncated so that it is not divided up into different
    separate lines by the syslog daemon (see #1043 and #1075)
  - The destination syslog daemon's configuration can be determined at runtime
    now by calling a configuration function (see #1049 and #1052)
```

## New Release Instructions

To actually perform a release, follow these steps:

  1. Increment the version number inside of `setup.py` and `timber/__init__.py` then commit it to `master`.
  2. Review existing documentation.
  3. Make sure that you have checked out `master` and have performed `git pull`.
  4. Create an annotated tag for the release.
  5. Push the new tags to GitHub using `git push --tags`
  6. Create a new release on the [GitHub
     releases](https://github.com/timberio/timber-python/releases) page. Use the
     tag you just created, with the first line of the tag's message as the title
     and the rest of the message as the body. Make sure to check the pre-release
     box if this is a release candidate.
  7. Run `python setup.py sdist bdist_wheel`
  8. Run `twine upload dist/*`

If you have any questions, ping @DavidAntaramian or @LucioFranco.
