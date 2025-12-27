#!/bin/bash
# ==============================================================================
# CLI Test Script for shai_tix
# ==============================================================================
# This script tests the shai-tix CLI by replicating the workflows from:
# - TestTixManageStory
# - TestTixManageTask
#
# Usage: Copy and paste commands manually or run the entire script.
# ==============================================================================

# Note: We don't use 'set -e' because some commands are expected to fail
# (e.g., get_story for deleted story, delete non-existent story)

echo "=============================================================================="
echo "Setup: Clean .tix directory"
echo "=============================================================================="
rm -rf .tix
mkdir -p .tix
echo "Created fresh .tix directory"
echo ""

echo "=============================================================================="
echo "Part 1: TestTixManageStory Workflow"
echo "=============================================================================="
echo ""

echo "--- Step 1: Create first story with description ---"
shai-tix create_story "First Story" --description "Description for first story."
echo ""

echo "--- Step 2: Verify story exists via get_story ---"
shai-tix get_story 1
echo ""

echo "--- Step 3: List all stories (should show 1 story) ---"
shai-tix list_stories
echo ""

echo "--- Step 4: Create second story ---"
shai-tix create_story "Second Story"
echo ""

echo "--- Step 5: Verify both stories exist ---"
shai-tix list_stories
echo ""

echo "--- Step 6: Search stories by title ---"
shai-tix search_stories --title "First"
echo ""

echo "--- Step 7: Delete first story ---"
shai-tix delete_story 1
echo ""

echo "--- Step 8: Verify first story is gone ---"
shai-tix get_story 1
echo ""

echo "--- Step 9: Verify second story remains ---"
shai-tix get_story 2
echo ""

echo "--- Step 10: List stories (should show only story 2) ---"
shai-tix list_stories
echo ""

echo "--- Step 11: Try delete non-existent story ---"
shai-tix delete_story 99999
echo ""

echo "--- Step 12: Try delete already deleted story ---"
shai-tix delete_story 1
echo ""

echo "=============================================================================="
echo "Part 2: Test update_story workflow"
echo "=============================================================================="
echo ""

echo "--- Create a story for update testing ---"
shai-tix create_story "Original Title"
echo ""

echo "--- Update story title (triggers folder rename) ---"
shai-tix update_story 3 --title "Renamed Title"
echo ""

echo "--- Verify story was renamed ---"
shai-tix get_story 3
echo ""

echo "--- Update story status, description, and report ---"
shai-tix update_story 3 --status "COMPLETED" --description "Updated description content." --report "Final report content."
echo ""

echo "--- Verify updates applied ---"
shai-tix get_story 3
echo ""

echo "--- Update story with title that sanitizes to same value ---"
shai-tix create_story "My Story"
shai-tix update_story 4 --title "My Story!"
shai-tix get_story 4
echo ""

echo "=============================================================================="
echo "Part 3: TestTixManageTask Workflow"
echo "=============================================================================="
echo ""

echo "--- Step 1: Create parent story for tasks ---"
shai-tix create_story "Parent Story"
echo ""

echo "--- Step 2: Create first task with description ---"
shai-tix create_task 5 "First Task" --description "Description for first task."
echo ""

echo "--- Step 3: Verify task exists via get_task ---"
shai-tix get_task 6
echo ""

echo "--- Step 4: Create second task ---"
shai-tix create_task 5 "Second Task"
echo ""

echo "--- Step 5: List tasks by story ---"
shai-tix list_tasks_by_story 5
echo ""

echo "--- Step 6: List all tasks ---"
shai-tix list_tasks
echo ""

echo "--- Step 7: Update first task (title, status, description, report) ---"
shai-tix update_task 6 --title "Updated First Task" --status "IN_PROGRESS" --description "Updated description." --report "Task progress report."
echo ""

echo "--- Step 8: Verify update applied ---"
shai-tix get_task 6
echo ""

echo "--- Step 9: Search tasks by title ---"
shai-tix search_tasks --title "Updated"
echo ""

echo "--- Step 10: Delete first task ---"
shai-tix delete_task 6
echo ""

echo "--- Step 11: Verify first task is gone ---"
shai-tix get_task 6
echo ""

echo "--- Step 12: Verify second task remains ---"
shai-tix get_task 7
echo ""

echo "--- Step 13: List tasks by story (should show only task 7) ---"
shai-tix list_tasks_by_story 5
echo ""

echo "--- Step 14: Try delete non-existent task ---"
shai-tix delete_task 99999
echo ""

echo "--- Step 15: Try delete already deleted task ---"
shai-tix delete_task 6
echo ""

echo "=============================================================================="
echo "Part 4: Test update_task with same sanitized title"
echo "=============================================================================="
echo ""

echo "--- Create story and task ---"
shai-tix create_story "Task Parent"
shai-tix create_task 8 "My Task"
echo ""

echo "--- Update task title to same sanitized value ---"
shai-tix update_task 9 --title "My Task!"
echo ""

echo "--- Verify task updated ---"
shai-tix get_task 9
echo ""

echo "=============================================================================="
echo "Part 5: Test delete_story cascades to tasks"
echo "=============================================================================="
echo ""

echo "--- Create story with tasks ---"
shai-tix create_story "Story To Delete"
shai-tix create_task 10 "Task A"
shai-tix create_task 10 "Task B"
echo ""

echo "--- Verify tasks exist ---"
shai-tix get_task 11
shai-tix get_task 12
echo ""

echo "--- Delete story (should cascade to tasks) ---"
shai-tix delete_story 10
echo ""

echo "--- Verify tasks are also deleted ---"
shai-tix get_task 11
shai-tix get_task 12
echo ""

echo "=============================================================================="
echo "Part 6: Test search functionality"
echo "=============================================================================="
echo ""

echo "--- Create stories for search testing ---"
shai-tix create_story "Login Feature Implementation"
shai-tix create_story "User Authentication"
shai-tix create_story "Database Migration"
echo ""

echo "--- Search by single token ---"
shai-tix search_stories --title "login"
echo ""

echo "--- Search by partial match ---"
shai-tix search_stories --title "user"
echo ""

echo "--- Search by ID range ---"
shai-tix search_stories --id_lower 13 --id_upper 14
echo ""

echo "--- Create tasks for search testing ---"
shai-tix create_task 13 "Write Unit Tests"
shai-tix create_task 13 "Write Integration Tests"
shai-tix create_task 13 "Fix Bug"
echo ""

echo "--- Search tasks by title ---"
shai-tix search_tasks --title "write"
echo ""

echo "--- Search tasks by different token ---"
shai-tix search_tasks --title "bug"
echo ""

echo "=============================================================================="
echo "Part 7: Test search by status"
echo "=============================================================================="
echo ""

echo "--- Create stories with different statuses ---"
shai-tix create_story "TODO Story One"
shai-tix update_story 19 --status "TODO"
shai-tix create_story "In Progress Story"
shai-tix update_story 20 --status "IN_PROGRESS"
shai-tix create_story "Completed Story"
shai-tix update_story 21 --status "COMPLETED"
shai-tix create_story "TODO Story Two"
shai-tix update_story 22 --status "TODO"
echo ""

echo "--- Search stories by single status (TODO) ---"
shai-tix search_stories --status "TODO"
echo ""

echo "--- Search stories by multiple statuses (TODO,IN_PROGRESS) ---"
shai-tix search_stories --status "TODO,IN_PROGRESS"
echo ""

echo "--- Search stories by status with no matches (BLOCKED) ---"
shai-tix search_stories --status "BLOCKED"
echo ""

echo "--- Search stories by status combined with title ---"
shai-tix search_stories --title "TODO" --status "TODO"
echo ""

echo "--- Create tasks with different statuses ---"
shai-tix create_task 19 "TODO Task One"
shai-tix update_task 23 --status "TODO"
shai-tix create_task 19 "In Progress Task"
shai-tix update_task 24 --status "IN_PROGRESS"
shai-tix create_task 19 "Completed Task"
shai-tix update_task 25 --status "COMPLETED"
shai-tix create_task 19 "TODO Task Two"
shai-tix update_task 26 --status "TODO"
echo ""

echo "--- Search tasks by single status (TODO) ---"
shai-tix search_tasks --status "TODO"
echo ""

echo "--- Search tasks by multiple statuses (TODO,IN_PROGRESS) ---"
shai-tix search_tasks --status "TODO,IN_PROGRESS"
echo ""

echo "--- Search tasks by status with limit ---"
shai-tix search_tasks --status "TODO" --limit 1
echo ""

echo "=============================================================================="
echo "CLI Test Complete!"
echo "=============================================================================="