<template>
    <div id="media-modal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="container">
                        <div class="row">
                            <div class="col-md-12">
                                <h3 class="text-center">Media Library</h3>
                            </div>
                        </div>
                    </div>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="modal-header">
                        <div class="container">
                            <div class="row mh-100">
                                <div class="col-md-6" id="media-library-list">
                                </div>
                                <div class="col-md-6" id="media-library-details">
                                    <h4 class="text-center">Media Details</h4>
                                    <div id="media-item">
                                        <div class="text-center" id="media-icon">
                                        </div>
                                        <br>
                                        <div class="text-center" id="media-filename">
                                        </div>
                                        <br>
                                        <div class="form-group">
                                            Link: <input class="form-control" type="text" id="media-link" readonly>
                                        </div>

                                        <div class="form-group text-center">
                                            <div class="row">
                                                <div class="col-md-6">
                                                    <button class="btn btn-success w-100" id="media-insert"
                                                            data-toggle="tooltip" data-placement="top"
                                                            title="Insert link into editor">
                                                        Insert
                                                    </button>
                                                </div>
                                                <div class="col-md-3">
                                                    <button class="btn btn-primary w-100" id="media-download"
                                                            data-toggle="tooltip" data-placement="top"
                                                            title="Download file">
                                                        <i class="fas fa-download"></i>
                                                    </button>
                                                </div>
                                                <div class="col-md-3">
                                                    <button class="btn btn-danger w-100" id="media-delete"
                                                            data-toggle="tooltip" data-placement="top"
                                                            title="Delete file">
                                                        <i class="far fa-trash-alt"></i>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <form id="media-library-upload" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="media-files">
                                Upload Files
                            </label>
                            <input type="file" name="file" id="media-files" class="form-control-file" multiple>
                            <sub class="help-block">
                                Attach multiple files using Control+Click or Cmd+Click.
                            </sub>
                        </div>
                        <input type="hidden" value="page" name="type">
                    </form>

                </div>
                <div class="modal-footer">
                    <div class="float-right">
                        <button type="submit" class="btn btn-primary media-upload-button">Upload</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
</script>