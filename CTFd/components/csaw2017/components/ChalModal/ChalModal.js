import Inferno from 'inferno';

import './ChalModal.scss';

export default props => {
  const { challenge, hide } = props;
  if (!challenge) {
    return <div className="chal-modal-container" />;
  }

  console.log(challenge);

  return (
    <div className="chal-modal-container open" onClick={hide}>
      <div className="chal-modal">
        <div className="chal-category">
          {challenge.category}
        </div>
        <div className="chal-name">
          {challenge.name}
        </div>
        <div className="chal-desc">
          {challenge.description}
        </div>
      </div>
    </div>
  );
};
