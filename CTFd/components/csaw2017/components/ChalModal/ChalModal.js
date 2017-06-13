import Inferno from 'inferno';
import Component from 'inferno-component';

import './ChalModal.scss';

export default class ChalModal extends Component {
  constructor(props) {
    super(props);

    this.state = {
      input: ''
    };

    this.onInputKeyDown = this.onInputKeyDown.bind(this);
    this.onInputChange = this.onInputChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.challenge != nextProps.challenge) {
      this.setState(state => {
        state.input = '';
      });
    }
  }

  onInputKeyDown(e) {
    if (e.key === 'Enter') {
      this.onSubmit();
    }

    if (e.key === 'Escape') {
      this.setState(state => {
        state.input = '';
      });
    }
  }

  onInputChange(e) {
    this.setState(state => {
      state.input = e.target.value;
    });
  }

  onSubmit() {
    if (!this.state.input.length) return;
    this.props.submit(this.state.input);
  }

  render() {
    const { challenge, hide, submit, response } = this.props;

    if (!challenge) {
      return <div className="chal-modal-container" />;
    }

    return (
      <div className="chal-modal-container open" onClick={hide}>
        <div className="chal-modal">
          <div className="chal-row">
            <div className="chal-category">
              {challenge.category}
            </div>
            <div className="chal-name">
              {challenge.name}
            </div>
            <div className="chal-desc">
              {challenge.description}
            </div>
            <div className="chal-files">
              {challenge.files.map(file =>
                <a className="chal-file" href={`/files/${file}`} download>{file.split('/').slice(-1)[0]}</a>
              )}
            </div>
          </div>
          <div className="chal-row">
            <div className="chal-input">
              <div className="chal-input-row">
                <input
                  className={'csaw-form-control ' + (response || '')}
                  type="text"
                  placeholder="Key"
                  onKeyDown={this.onInputKeyDown}
                  onInput={this.onInputChange}
                  value={this.state.input}
                />
                <button className="btn btn-primary" onClick={this.onSubmit}>Submit</button>
              </div>
              <div className="chal-input-row">
                <div className={'chal-response ' + (response || '')}>
                  Key Rejected
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
