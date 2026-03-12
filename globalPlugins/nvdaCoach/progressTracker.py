# NVDA Coach - Progress Tracker
# Saves and loads lesson completion data for the current user.

import os
import json
import globalVars
from logHandler import log
from datetime import datetime


class ProgressTracker:
	"""Manages persistent storage of lesson progress."""

	def __init__(self):
		self._progressFile = os.path.join(
			globalVars.appArgs.configPath, "nvdaCoachProgress.json"
		)
		self._data = self._load()

	def _load(self):
		"""Load progress data from disk."""
		try:
			if os.path.exists(self._progressFile):
				with open(self._progressFile, "r", encoding="utf-8") as f:
					return json.load(f)
		except Exception as e:
			log.warning(f"NVDA Coach: Could not load progress file: {e}")
		return {}

	def _save(self):
		"""Write progress data to disk."""
		try:
			with open(self._progressFile, "w", encoding="utf-8") as f:
				json.dump(self._data, f, indent=2, ensure_ascii=False)
		except Exception as e:
			log.error(f"NVDA Coach: Could not save progress file: {e}")

	def markLessonComplete(self, categoryId, lessonId, attempts, totalSteps):
		"""Record that a lesson was completed.

		Args:
			categoryId: The ID of the lesson category (e.g. "getting_started").
			lessonId: The ID of the specific lesson (e.g. "title_bar").
			attempts: Dict mapping step keys to attempt counts.
			totalSteps: Total number of steps in the lesson.
		"""
		if categoryId not in self._data:
			self._data[categoryId] = {}
		firstTryCount = sum(1 for v in attempts.values() if v == 1)
		self._data[categoryId][lessonId] = {
			"completed": True,
			"completedDate": datetime.now().isoformat(),
			"attempts": attempts,
			"firstTryCount": firstTryCount,
			"totalSteps": totalSteps,
		}
		self._save()

	def isLessonComplete(self, categoryId, lessonId):
		"""Check whether a lesson has been completed before."""
		category = self._data.get(categoryId, {})
		lesson = category.get(lessonId, {})
		return lesson.get("completed", False)

	def getLessonResult(self, categoryId, lessonId):
		"""Return the stored result for a lesson, or None."""
		category = self._data.get(categoryId, {})
		return category.get(lessonId, None)

	def getCategoryProgress(self, categoryId, totalLessons):
		"""Return (completed_count, total) for a category."""
		category = self._data.get(categoryId, {})
		completed = sum(1 for v in category.values() if v.get("completed"))
		return completed, totalLessons

	def resetProgress(self):
		"""Clear all progress data."""
		self._data = {}
		self._save()
