import Inferno from 'inferno';
import Component from 'inferno-component';

import './ChalProgress.scss';

export default class ChalProgress extends Component {
  constructor(props) {
    super(props);

    this.state = {
      progressBarPctStr: '0'
    };
  }

  componentDidMount() {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        this.setState(state => {
          state.progressBarPctStr = '13.3%';
        });
      });
    });
  }

  render() {
    return (
      <div className="chal-progress">
        <span className="progress-pct">13.3%</span><span className="progress-pts">(4,000 / 30,000)</span>
        <div className="progress-bar-bg" />
        <div className="progress-bar" style={{ width: this.state.progressBarPctStr }} />
      </div>
    );
  }
}
