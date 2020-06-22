import $ from "jquery";
import CTFd from "core/CTFd";

export function deleteTag(_event) {
  const $elem = $(this);
  const tag_id = $elem.attr("tag-id");

  CTFd.api.delete_tag({ tagId: tag_id }).then(response => {
    if (response.success) {
      $elem.parent().remove();
    }
  });
}

export function addTag(event) {
  if (event.keyCode != 13) {
    return;
  }

  const $elem = $(this);

  const tag = $elem.val();
  const params = {
    value: tag,
    challenge: window.CHALLENGE_ID
  };

  CTFd.api.post_tag_list({}, params).then(response => {
    if (response.success) {
      const tpl =
        "<span class='badge badge-primary mx-1 challenge-tag'>" +
        "<span>{0}</span>" +
        "<a class='btn-fa delete-tag' tag-id='{1}'>&times;</a></span>";
      const tag = $(tpl.format(response.data.value, response.data.id));
      $("#challenge-tags").append(tag);
      // TODO: tag deletion not working on freshly created tags
      tag.click(deleteTag);
    }
  });

  $elem.val("");
}
