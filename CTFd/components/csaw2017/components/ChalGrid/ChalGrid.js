import Inferno from 'inferno';

import './ChalGrid.scss';

export default props => {
  const range = props.challenges.reduce(
    (obj, chal) => {
      if (!obj.min) {
        obj.min = chal.value;
      }

      if (!obj.max) {
        obj.max = chal.value;
      }

      if (chal.value > obj.max) {
        obj.max = chal.value;
      }

      if (chal.value < obj.min) {
        obj.min = chal.value;
      }

      return obj;
    },
    { min: null, max: null }
  );
  console.log(range);

  return (
    <div className="chal-grid">
      {props.challenges.map(chal => {
        return (
          <div className="chal-item-container" onClick={e => console.log(e)}>
            <div className="chal-item">
              <div className="chal-title">
                {chal.category}
              </div>
              <div className="chal-name">
                {chal.name}
                {' '}{Math.random() > 0.5 ? "is a really long challenege name but i guess we don't really care" : ''}
              </div>
              <div className="chal-points" style={{ color: getColorFromValue(chal.value, range) }}>
                {chal.value}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

function getColorFromValue (value, range) {
  const h = 240 * (1 - (value - range.min) / (range.max - range.min));
  return 'hsl(' + Math.floor(h) + ', 91%, 43.5%)';
};
