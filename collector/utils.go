package main

import (
	"fmt"
	"os"
)

// Version infomation
var (
	// InsightGitBranch is initialized during make
	InsightGitBranch = "Not Provided"

	// InsightGitCommit is initialized during make
	InsightGitCommit = "Not Provided"

	// InsightBuildDate is initialized during make
	InsightBuildTime = "Not Provided"
)

func printErr(err error) {
	if err == nil {
		return
	}
	fmt.Fprintf(os.Stderr, err.Error())
}
