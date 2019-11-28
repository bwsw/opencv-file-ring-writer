# Video stream copying to a ring buffer of files with fixed duration using OpenCV, Python, and ZeroMQ

The problem described in this article is often met in intelligent video analytics solutions. In general, a user wants to get an access to a fragment that contains some identified events. A fragment is a set of one or more small video files that contain both the event itself and the history and development of the situation associated with it.

It is convenient to solve this task with a ring buffer of video fragments, presented by small files, for example, for 30 seconds. So, when the application detects that some of them contain important signals, it copies the files that include the signal from the ring buffer into the permanent storage. The buffer is a ring because old files are deleted from the disk (for example, after 10 minutes have passed), so the buffer always takes a fixed amount of space on the storage.

You will learn how to develop such a ring buffer, which connects to the main video processing pipeline and manages the creation and deletion of video files that form the buffer. To solve the problem OpenCV, Python, LZ4, and ZeroMQ will be used. For simplicity, we assume that the FPS for video files is the same as FPS of a stream, that is, all video frames from the stream are written to files. In real implementations, removal of redundant frames from a stream, a change in resolution, etc., may take place.

Read more: [https://bitworks.software/en/opencv-stream-write-splitted-video-files.html](https://bitworks.software/en/opencv-stream-write-splitted-video-files.html)
